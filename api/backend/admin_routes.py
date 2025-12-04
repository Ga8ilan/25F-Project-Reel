from flask import Blueprint, jsonify, request
#blueprint for admin routes

#APPLICATION REVIEW ROUTES 

@admin_bp.get("applications")
def get_applications(): 
    """
    List pending/approved applications for admin review.
    [William-1]
    """
    # TODO: SELECT * FROM Applications WHERE status IN(...)
    return jsonify({"message": "stub GET /applications"}), 200

@admin_bp.get("/applications/int:application_id>")
def get_application_details(application_id)
    """
    Get full details for a specific application. 
    [William-2]
    """
    # TODO: SELECT * FROM Applications WHERE applicationID = ?
    return jsonify({
        "application_id": application_id,
        "message": "stub GET /applications/<id>"
    }), 200

@admin_bp.put("/applications/<int:application_id>")
def update_application_status(application_id):
    """
    Update application status (approve/reject/request-info).
    [William-2]
    """
    data = request.get_json(silent=True) or {}
    # TODO: UPDATE Applications SET status = ?
    return jsonify({
        "application_id": application_id, 
        "status_change": data, 
        "message": "stub PUT /applications/<id>"
    }), 200

#FLAGGED ACTIVITIES 

@admin_bp.get("/flagged-activities")
def list_flagged_activities():
    """
    Return flagged content/accounts needing review.
    [William-4]
    """
    # TODO: SELECT * FROM FlaggedActivity
    return jsonify({"message": "stub GET /flagged-activities"}), 200

#SYSTEM HEALTH 

@admin_bp.get("/system-metrics")
def get_system_metrics():
    """
    Get system performance metrics. 
    [William-3]
    """
    # TODO: SELECT * FROM SystemMetrics or return dummy health info 
    return jsonify({"status": "ok", "message": "stub GET /system-metrics"}), 200