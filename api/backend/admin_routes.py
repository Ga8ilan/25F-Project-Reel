from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import db

admin_bp = Blueprint("admin", __name__)

# DB helper

def get_dict_cursor():
    """
    Get a connection + cursor that returns rows as dictionaries.
    """
    conn = db.get_db()
    cursor = conn.cursor()
    return conn, cursor


# /applications
# REST Matrix: GET /applications

@admin_bp.get("/applications")
def get_applications():
    """
    List pending/approved applications for admin review.
    Matrix: GET /applications – [William-1]
    """
    try:
        conn, cursor = get_dict_cursor()

        # Optional filter: ?status=pending,approved,rejected,needs-info
        status_param = request.args.get("status")
        if status_param:
            statuses = [s.strip() for s in status_param.split(",") if s.strip()]
        else:
            # Matrix text says "pending/approved" by default
            statuses = ["pending", "approved"]

        placeholders = ", ".join(["%s"] * len(statuses))

        query = f"""
            SELECT
                application_id,
                applicant_name,
                email,
                portfolio_url,
                status,
                submitted_at,
                last_updated_at,
                admin_notes
            FROM Applications
            WHERE status IN ({placeholders})
            ORDER BY submitted_at DESC
        """

        cursor.execute(query, statuses)
        applications = cursor.fetchall()

        return jsonify({"applications": applications}), 200

    except Exception:
        current_app.logger.exception("Error fetching applications")
        return jsonify({"error": "Failed to fetch applications"}), 500


# /applications/{applicationID}
# REST Matrix: GET/PUT/DELETE /applications/{applicationID}

@admin_bp.get("/applications/<int:application_id>")
def get_application_details(application_id):
    """
    Get full details for a specific application.
    Matrix: GET /applications/{applicationID} – [William-1], [William-2]
    """
    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            SELECT
                application_id,
                applicant_name,
                email,
                portfolio_url,
                status,
                submitted_at,
                last_updated_at,
                admin_notes
            FROM Applications
            WHERE application_id = %s
            """,
            (application_id,),
        )
        application = cursor.fetchone()

        if application is None:
            return jsonify({"error": "Application not found"}), 404

        return jsonify(application), 200

    except Exception:
        current_app.logger.exception(
            "Error fetching application details for id %s", application_id
        )
        return jsonify({"error": "Failed to fetch application details"}), 500


@admin_bp.put("/applications/<int:application_id>")
def update_application_status(application_id):
    """
    Update application status (approved/rejected/needs-info) and notes.
    Matrix: PUT /applications/{applicationID} – [William-2]
    Request JSON:
      {
        "status": "approved" | "rejected" | "needs-info" | "pending",
        "admin_notes": "optional notes"
      }
    """
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    admin_notes = data.get("admin_notes")

    if not new_status:
        return jsonify({"error": "Missing required field: 'status'"}), 400

    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            UPDATE Applications
            SET status = %s,
                admin_notes = COALESCE(%s, admin_notes),
                last_updated_at = NOW()
            WHERE application_id = %s
            """,
            (new_status, admin_notes, application_id),
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Application not found"}), 404

        conn.commit()

        # Return updated record
        cursor.execute(
            """
            SELECT
                application_id,
                applicant_name,
                email,
                portfolio_url,
                status,
                submitted_at,
                last_updated_at,
                admin_notes
            FROM Applications
            WHERE application_id = %s
            """,
            (application_id,),
        )
        updated = cursor.fetchone()

        return jsonify(updated), 200

    except Exception:
        current_app.logger.exception(
            "Error updating application status for id %s", application_id
        )
        return jsonify({"error": "Failed to update application"}), 500


@admin_bp.delete("/applications/<int:application_id>")
def delete_application(application_id):
    """
    Soft-archive an application so it leaves the active review queue.
    Matrix: DELETE /applications/{applicationID} – [William-1]
    Implementation note:
      For now this is implemented as a hard delete in the DB. If your
      schema later adds an 'is_archived' flag, this SQL can be changed
      to an UPDATE without changing the route.
    """
    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            "DELETE FROM Applications WHERE application_id = %s",
            (application_id,),
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Application not found"}), 404

        conn.commit()

        return jsonify(
            {
                "application_id": application_id,
                "message": "Application removed from active review queue",
            }
        ), 200

    except Exception:
        current_app.logger.exception(
            "Error deleting application with id %s", application_id
        )
        return jsonify({"error": "Failed to delete application"}), 500


# /flagged-activities (collection + single)
# REST Matrix: GET/POST/PUT/DELETE /flagged-activities

@admin_bp.get("/flagged-activities")
def list_flagged_activities():
    """
    List flagged items (posts, portfolios, projects, messages) needing review.
    Matrix: GET /flagged-activities – [William-4], [William-7]
    """
    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            SELECT
                flag_id,
                related_type,
                related_id,
                reason,
                status,
                resolution_notes,
                created_at,
                resolved_at
            FROM FlaggedActivities
            ORDER BY created_at DESC
            """
        )
        flagged = cursor.fetchall()

        return jsonify({"flagged_activities": flagged}), 200

    except Exception:
        current_app.logger.exception("Error fetching flagged activities")
        return jsonify({"error": "Failed to fetch flagged activities"}), 500


@admin_bp.post("/flagged-activities")
def create_flagged_activity():
    """
    Create a new flagged-activity record (user report or automated flag).
    Matrix: POST /flagged-activities – [William-4]
    Request JSON:
      {
        "related_type": "post" | "portfolio" | "project" | "message" | ...,
        "related_id": 123,
        "reason": "why it was flagged",
        "status": "open" | "in-review" | "resolved"   (optional, default 'open')
      }
    """
    data = request.get_json(silent=True) or {}

    related_type = data.get("related_type")
    related_id = data.get("related_id")
    reason = data.get("reason")
    status = data.get("status") or "open"

    if not (related_type and related_id and reason):
        return jsonify(
            {"error": "Missing required fields: 'related_type', 'related_id', 'reason'"}
        ), 400

    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            INSERT INTO FlaggedActivities
                (related_type, related_id, reason, status)
            VALUES (%s, %s, %s, %s)
            """,
            (related_type, related_id, reason, status),
        )

        flag_id = cursor.lastrowid
        conn.commit()

        cursor.execute(
            """
            SELECT
                flag_id,
                related_type,
                related_id,
                reason,
                status,
                resolution_notes,
                created_at,
                resolved_at
            FROM FlaggedActivities
            WHERE flag_id = %s
            """,
            (flag_id,),
        )
        new_flag = cursor.fetchone()

        return jsonify(new_flag), 201

    except Exception:
        current_app.logger.exception("Error creating flagged activity")
        return jsonify({"error": "Failed to create flagged activity"}), 500


@admin_bp.put("/flagged-activities/<int:flag_id>")
def update_flagged_activity(flag_id):
    """
    Update review status and resolution on a flag.
    Matrix: PUT /flagged-activities/{flagID} – [William-4]
    Request JSON:
      {
        "status": "open" | "in-review" | "resolved" | "dismissed",
        "resolution_notes": "optional notes"
      }
    """
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    resolution_notes = data.get("resolution_notes")

    if not new_status and resolution_notes is None:
        return jsonify({"error": "Nothing to update"}), 400

    try:
        conn, cursor = get_dict_cursor()

        updates = []
        params = []

        if new_status:
            updates.append("status = %s")
            params.append(new_status)

        if resolution_notes is not None:
            updates.append("resolution_notes = %s")
            params.append(resolution_notes)

        # If status is resolved, set resolved_at timestamp
        if new_status == "resolved":
            updates.append("resolved_at = NOW()")

        if not updates:
            return jsonify({"error": "Nothing to update"}), 400

        params.append(flag_id)

        query = f"""
            UPDATE FlaggedActivities
            SET {", ".join(updates)}
            WHERE flag_id = %s
        """

        cursor.execute(query, params)

        if cursor.rowcount == 0:
            return jsonify({"error": "Flagged activity not found"}), 404

        conn.commit()

        cursor.execute(
            """
            SELECT
                flag_id,
                related_type,
                related_id,
                reason,
                status,
                resolution_notes,
                created_at,
                resolved_at
            FROM FlaggedActivities
            WHERE flag_id = %s
            """,
            (flag_id,),
        )
        updated_flag = cursor.fetchone()

        return jsonify(updated_flag), 200

    except Exception:
        current_app.logger.exception(
            "Error updating flagged activity with id %s", flag_id
        )
        return jsonify({"error": "Failed to update flagged activity"}), 500


@admin_bp.delete("/flagged-activities/<int:flag_id>")
def delete_flagged_activity(flag_id):
    """
    Remove a flag created in error or no longer relevant.
    Matrix: DELETE /flagged-activities/{flagID} – [William-4]
    """
    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            "DELETE FROM FlaggedActivities WHERE flag_id = %s",
            (flag_id,),
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Flagged activity not found"}), 404

        conn.commit()

        return jsonify(
            {
                "flag_id": flag_id,
                "message": "Flagged activity removed",
            }
        ), 200

    except Exception:
        current_app.logger.exception(
            "Error deleting flagged activity with id %s", flag_id
        )
        return jsonify({"error": "Failed to delete flagged activity"}), 500


# /alerts (collection + single)
# REST Matrix: GET/POST/PUT/DELETE /alerts

@admin_bp.get("/alerts")
def list_alerts():
    """
    List active system/moderation alerts for the admin dashboard.
    Matrix: GET /alerts – [William-4], [William-7]
    """
    try:
        conn, cursor = get_dict_cursor()

        # Active = not fully archived; adjust based on your schema later.
        cursor.execute(
            """
            SELECT
                alert_id,
                alert_type,
                related_type,
                related_id,
                message,
                status,
                admin_notes,
                created_at,
                resolved_at
            FROM Alerts
            WHERE status IN ('open', 'acknowledged', 'resolved')
            ORDER BY created_at DESC
            """
        )
        alerts = cursor.fetchall()

        return jsonify({"alerts": alerts}), 200

    except Exception:
        current_app.logger.exception("Error fetching alerts")
        return jsonify({"error": "Failed to fetch alerts"}), 500


@admin_bp.post("/alerts")
def create_alert():
    """
    Create a new alert from monitoring/base detection.
    Matrix: POST /alerts – [William-4]
    Request JSON:
      {
        "alert_type": "system" | "moderation" | ...,
        "message": "description of the alert",
        "related_type": "optional related entity type",
        "related_id": 123   (optional)
      }
    """
    data = request.get_json(silent=True) or {}

    alert_type = data.get("alert_type")
    message = data.get("message")
    related_type = data.get("related_type")
    related_id = data.get("related_id")

    if not (alert_type and message):
        return jsonify({"error": "Missing required fields: 'alert_type', 'message'"}), 400

    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            INSERT INTO Alerts
                (alert_type, message, related_type, related_id, status)
            VALUES (%s, %s, %s, %s, 'open')
            """,
            (alert_type, message, related_type, related_id),
        )

        alert_id = cursor.lastrowid
        conn.commit()

        cursor.execute(
            """
            SELECT
                alert_id,
                alert_type,
                related_type,
                related_id,
                message,
                status,
                admin_notes,
                created_at,
                resolved_at
            FROM Alerts
            WHERE alert_id = %s
            """,
            (alert_id,),
        )
        new_alert = cursor.fetchone()

        return jsonify(new_alert), 201

    except Exception:
        current_app.logger.exception("Error creating alert")
        return jsonify({"error": "Failed to create alert"}), 500


@admin_bp.put("/alerts/<int:alert_id>")
def update_alert(alert_id):
    """
    Update alert status (acknowledged/resolved) and notes.
    Matrix: PUT /alerts/{alertID} – [William-4]
    Request JSON:
      {
        "status": "open" | "acknowledged" | "resolved" | "dismissed",
        "admin_notes": "optional notes"
      }
    """
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    admin_notes = data.get("admin_notes")

    if not new_status and admin_notes is None:
        return jsonify({"error": "Nothing to update"}), 400

    try:
        conn, cursor = get_dict_cursor()

        updates = []
        params = []

        if new_status:
            updates.append("status = %s")
            params.append(new_status)

        if admin_notes is not None:
            updates.append("admin_notes = %s")
            params.append(admin_notes)

        if new_status == "resolved":
            updates.append("resolved_at = NOW()")

        if not updates:
            return jsonify({"error": "Nothing to update"}), 400

        params.append(alert_id)

        query = f"""
            UPDATE Alerts
            SET {", ".join(updates)}
            WHERE alert_id = %s
        """

        cursor.execute(query, params)

        if cursor.rowcount == 0:
            return jsonify({"error": "Alert not found"}), 404

        conn.commit()

        cursor.execute(
            """
            SELECT
                alert_id,
                alert_type,
                related_type,
                related_id,
                message,
                status,
                admin_notes,
                created_at,
                resolved_at
            FROM Alerts
            WHERE alert_id = %s
            """,
            (alert_id,),
        )
        updated_alert = cursor.fetchone()

        return jsonify(updated_alert), 200

    except Exception:
        current_app.logger.exception(
            "Error updating alert with id %s", alert_id
        )
        return jsonify({"error": "Failed to update alert"}), 500


@admin_bp.delete("/alerts/<int:alert_id>")
def delete_alert(alert_id):
    """
    Archive/delete resolved alerts after resolution.
    Matrix: DELETE /alerts/{alertID} – [William-4]
    Implementation note:
      Currently implemented as a hard delete. If your schema later adds
      an 'is_archived' flag, this can become an UPDATE instead.
    """
    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            "DELETE FROM Alerts WHERE alert_id = %s",
            (alert_id,),
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Alert not found"}), 404

        conn.commit()

        return jsonify(
            {
                "alert_id": alert_id,
                "message": "Alert removed",
            }
        ), 200

    except Exception:
        current_app.logger.exception(
            "Error deleting alert with id %s", alert_id
        )
        return jsonify({"error": "Failed to delete alert"}), 500


# /system-metrics
# REST Matrix: GET /system-metrics

@admin_bp.get("/system-metrics")
def get_system_metrics():
    """
    Return high-level system metrics for the admin dashboard.
    Matrix: GET /system-metrics – [William-3]
    Currently returns counts derived from existing tables.
    """
    try:
        conn, cursor = get_dict_cursor()

        # Total applications
        cursor.execute("SELECT COUNT(*) AS count FROM Applications")
        total_apps = cursor.fetchone()["count"]

        # Pending applications
        cursor.execute(
            "SELECT COUNT(*) AS count FROM Applications WHERE status = %s",
            ("pending",),
        )
        pending_apps = cursor.fetchone()["count"]

        # Approved applications
        cursor.execute(
            "SELECT COUNT(*) AS count FROM Applications WHERE status = %s",
            ("approved",),
        )
        approved_apps = cursor.fetchone()["count"]

        # Open flagged activities
        cursor.execute(
            "SELECT COUNT(*) AS count FROM FlaggedActivities WHERE status = %s",
            ("open",),
        )
        open_flags = cursor.fetchone()["count"]

        return jsonify(
            {
                "status": "ok",
                "metrics": {
                    "total_applications": total_apps,
                    "pending_applications": pending_apps,
                    "approved_applications": approved_apps,
                    "open_flags": open_flags,
                },
            }
        ), 200

    except Exception:
        current_app.logger.exception("Error computing system metrics")
        return jsonify(
            {
                "status": "degraded",
                "metrics": {},
                "message": "Unable to compute metrics",
            }
        ), 500