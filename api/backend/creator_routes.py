from flask import Blueprint, jsonify, request

creator_bp = Blueprint("creator", __name__)

# Portfolios: 

@creator_bp.get("/portfolios")
def list_portfolios():
    """
    List creator portfolios.
    """
    return jsonify({"message": "stub GET /portfolios"}), 200

@creator_bp.post("/portfolios")
def create_portfolio():
    """
    Create a new portfolio.
    """
    data = request.get_json(silent=True) or {}
    return jsonify({"message": "stub POST /portfolios", "received": data}), 201

# Projects: 

@creator_bp.get("/projects")
def list_project():
    """
    List projects in the system.
    """
    return jsonify({"message": "stub GET /projects"}), 200

@creator_bp.post("/projects")
def create_project():
    """
    Create a new project. 
    """
    data = request.get_json(silent=True) or {}
    return jsonify({"message": "stub POST /projects", "received": data}), 201
    
@creator_bp.put("/projects/<int:project_id>")
def update_project(project_id):
    """
    Update an existing project.
    """
    data = request.get_json(silent=True) or {}
    return jsonify({"message": "stub PUT /projects<id>", "project_id": project_id, "updates": data}), 200

