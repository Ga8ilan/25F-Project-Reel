from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import db

analytics_bp = Blueprint("analytics", __name__)

def get_dict_cursor():
    conn = db.get_db()
    cursor = conn.cursor()
    return conn, cursor

# TREND TAGS

@analytics_bp.get("/trend-tags")
def list_trend_tags():
    try:
        conn, cursor = get_dict_cursor()
        cursor.execute("""
            SELECT tag_id, tag_name, description, usage_count, status, created_at
            FROM TrendTags
            WHERE status != 'archived'
            ORDER BY usage_count DESC
        """)
        tags = cursor.fetchall()
        return jsonify({"trend_tags": tags}), 200
    except Exception:
        current_app.logger.exception("Error listing trend tags")
        return jsonify({"error": "Failed to fetch trend tags"}), 500


@analytics_bp.post("/trend-tags")
def create_trend_tag():
    data = request.get_json(silent=True) or {}
    name = data.get("tag_name")
    description = data.get("description")

    if not name:
        return jsonify({"error": "Missing required field: tag_name"}), 400

    try:
        conn, cursor = get_dict_cursor()
        cursor.execute("""
            INSERT INTO TrendTags (tag_name, description)
            VALUES (%s, %s)
        """, (name, description))
        tag_id = cursor.lastrowid
        conn.commit()

        cursor.execute("SELECT * FROM TrendTags WHERE tag_id = %s", (tag_id,))
        tag = cursor.fetchone()
        return jsonify(tag), 201
    except Exception:
        current_app.logger.exception("Error creating trend tag")
        return jsonify({"error": "Failed to create tag"}), 500


@analytics_bp.put("/trend-tags/<int:tag_id>")
def update_trend_tag(tag_id):
    data = request.get_json(silent=True) or {}
    name = data.get("tag_name")
    description = data.get("description")
    status = data.get("status")

    try:
        conn, cursor = get_dict_cursor()

        cursor.execute("""
            UPDATE TrendTags
            SET tag_name = COALESCE(%s, tag_name),
                description = COALESCE(%s, description),
                status = COALESCE(%s, status)
            WHERE tag_id = %s
        """, (name, description, status, tag_id))

        if cursor.rowcount == 0:
            return jsonify({"error": "Tag not found"}), 404

        conn.commit()

        cursor.execute("SELECT * FROM TrendTags WHERE tag_id = %s", (tag_id,))
        updated = cursor.fetchone()
        return jsonify(updated), 200
    except Exception:
        current_app.logger.exception("Error updating trend tag")
        return jsonify({"error": "Failed to update tag"}), 500


@analytics_bp.delete("/trend-tags/<int:tag_id>")
def delete_trend_tag(tag_id):
    try:
        conn, cursor = get_dict_cursor()
        cursor.execute("UPDATE TrendTags SET status='archived' WHERE tag_id=%s", (tag_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Tag not found"}), 404

        conn.commit()
        return jsonify({"message": "Tag archived"}), 200
    except Exception:
        current_app.logger.exception("Error archiving tag")
        return jsonify({"error": "Failed to delete tag"}), 500


# KPIS

@analytics_bp.get("/kpis")
def list_kpis():
    try:
        conn, cursor = get_dict_cursor()
        cursor.execute("SELECT * FROM Kpis WHERE status != 'archived'")
        return jsonify({"kpis": cursor.fetchall()}), 200
    except Exception:
        current_app.logger.exception("Error fetching KPIs")
        return jsonify({"error": "Failed to fetch KPIs"}), 500


@analytics_bp.post("/kpis")
def create_kpi():
    data = request.get_json(silent=True) or {}
    name = data.get("kpi_name")
    formula = data.get("formula")

    if not (name and formula):
        return jsonify({"error": "Missing fields"}), 400

    try:
        conn, cursor = get_dict_cursor()
        cursor.execute("""
            INSERT INTO Kpis (kpi_name, formula)
            VALUES (%s, %s)
        """, (name, formula))
        kpi_id = cursor.lastrowid
        conn.commit()

        cursor.execute("SELECT * FROM Kpis WHERE kpi_id = %s", (kpi_id,))
        return jsonify(cursor.fetchone()), 201
    except Exception:
        current_app.logger.exception("Error creating KPI")
        return jsonify({"error": "Failed to create KPI"}), 500


@analytics_bp.put("/kpis/<int:kpi_id>")
def update_kpi(kpi_id):
    data = request.get_json(silent=True) or {}

    try:
        conn, cursor = get_dict_cursor()

        cursor.execute("""
            UPDATE Kpis
            SET kpi_name = COALESCE(%s, kpi_name),
                formula = COALESCE(%s, formula),
                status = COALESCE(%s, status)
            WHERE kpi_id = %s
        """, (data.get("kpi_name"), data.get("formula"),
              data.get("status"), kpi_id))

        if cursor.rowcount == 0:
            return jsonify({"error": "KPI not found"}), 404

        conn.commit()
        cursor.execute("SELECT * FROM Kpis WHERE kpi_id = %s", (kpi_id,))
        return jsonify(cursor.fetchone()), 200

    except Exception:
        current_app.logger.exception("Error updating KPI")
        return jsonify({"error": "Failed to update KPI"}), 500


@analytics_bp.delete("/kpis/<int:kpi_id>")
def delete_kpi(kpi_id):
    try:
        conn, cursor = get_dict_cursor()
        cursor.execute("UPDATE Kpis SET status='archived' WHERE kpi_id=%s", (kpi_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "KPI not found"}), 404
        conn.commit()
        return jsonify({"message": "KPI archived"}), 200
    except Exception:
        current_app.logger.exception("Error archiving KPI")
        return jsonify({"error": "Failed to delete KPI"}), 500


# INSIGHT REPORTS

@analytics_bp.get("/insight-reports")
def list_reports():
    try:
        conn, cursor = get_dict_cursor()
        cursor.execute("""
            SELECT report_id, title, tags, sharing_scope, created_at
            FROM InsightReports
            ORDER BY created_at DESC
        """)
        return jsonify({"insight_reports": cursor.fetchall()}), 200
    except Exception:
        current_app.logger.exception("Error listing reports")
        return jsonify({"error": "Failed to fetch reports"}), 500


@analytics_bp.post("/insight-reports")
def create_report():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    tags = data.get("tags")
    report_data = data.get("report_data") or "{}"  # simple JSON string placeholder

    if not title:
        return jsonify({"error": "Missing required title"}), 400

    try:
        conn, cursor = get_dict_cursor()
        cursor.execute("""
            INSERT INTO InsightReports (title, tags, report_data)
            VALUES (%s, %s, %s)
        """, (title, tags, report_data))

        report_id = cursor.lastrowid
        conn.commit()

        cursor.execute("SELECT * FROM InsightReports WHERE report_id=%s", (report_id,))
        return jsonify(cursor.fetchone()), 201
    except Exception:
        current_app.logger.exception("Error creating insight report")
        return jsonify({"error": "Failed to create report"}), 500


@analytics_bp.put("/insight-reports/<int:report_id>")
def update_report(report_id):
    data = request.get_json(silent=True) or {}

    try:
        conn, cursor = get_dict_cursor()
        cursor.execute("""
            UPDATE InsightReports
            SET title = COALESCE(%s, title),
                tags = COALESCE(%s, tags),
                sharing_scope = COALESCE(%s, sharing_scope)
            WHERE report_id = %s
        """, (data.get("title"), data.get("tags"),
              data.get("sharing_scope"), report_id))

        if cursor.rowcount == 0:
            return jsonify({"error": "Report not found"}), 404

        conn.commit()

        cursor.execute("SELECT * FROM InsightReports WHERE report_id=%s", (report_id,))
        return jsonify(cursor.fetchone()), 200

    except Exception:
        current_app.logger.exception("Error updating report")
        return jsonify({"error": "Failed to update report"}), 500


@analytics_bp.delete("/insight-reports/<int:report_id>")
def delete_report(report_id):
    try:
        conn, cursor = get_dict_cursor()
        cursor.execute("""
            DELETE FROM InsightReports WHERE report_id = %s
        """, (report_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Report not found"}), 404

        conn.commit()
        return jsonify({"message": "Report deleted"}), 200
    except Exception:
        current_app.logger.exception("Error deleting report")
        return jsonify({"error": "Failed to delete report"}), 500