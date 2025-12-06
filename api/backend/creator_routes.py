from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import db

creator_bp = Blueprint("creator", __name__)

# DB helper
def get_dict_cursor():
    conn = db.get_db()
    cursor = conn.cursor()
    return conn, cursor


# PORTFOLIOS (multiple portfolios)
@creator_bp.get("/portfolios")
def list_portfolios():
    """
    List portfolios with optional filters.
    Matrix: GET /portfolios
    """
    try:
        conn, cursor = get_dict_cursor()

        # Basic example: allow ?user_id=#
        user_filter = request.args.get("user_id")

        if user_filter:
            cursor.execute(
                """
                SELECT portfolio_id, user_id, headline, bio,
                       featured_projects, is_archived, created_at
                FROM Portfolios
                WHERE user_id = %s AND is_archived = FALSE
                """,
                (user_filter,),
            )
        else:
            cursor.execute(
                """
                SELECT portfolio_id, user_id, headline, bio,
                       featured_projects, is_archived, created_at
                FROM Portfolios
                WHERE is_archived = FALSE
                """
            )

        return jsonify({"portfolios": cursor.fetchall()}), 200

    except Exception:
        current_app.logger.exception("Error listing portfolios")
        return jsonify({"error": "Failed to list portfolios"}), 500


@creator_bp.post("/portfolios")
def create_portfolio():
    """
    Create a new portfolio shell.
    Matrix: POST /portfolios
    """
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    headline = data.get("headline")
    bio = data.get("bio")

    if not user_id:
        return jsonify({"error": "Missing required field: user_id"}), 400

    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            INSERT INTO Portfolios (user_id, headline, bio)
            VALUES (%s, %s, %s)
            """,
            (user_id, headline, bio),
        )
        portfolio_id = cursor.lastrowid
        conn.commit()

        cursor.execute(
            """
            SELECT portfolio_id, user_id, headline, bio,
                   featured_projects, is_archived, created_at
            FROM Portfolios
            WHERE portfolio_id = %s
            """,
            (portfolio_id,),
        )
        return jsonify(cursor.fetchone()), 201

    except Exception:
        current_app.logger.exception("Error creating portfolio")
        return jsonify({"error": "Failed to create portfolio"}), 500


# PORTFOLIO
@creator_bp.get("/portfolios/<int:portfolio_id>")
def get_portfolio(portfolio_id):
    """
    Matrix: GET /portfolios/{portfolioID}
    """
    try:
        conn, cursor = get_dict_cursor()
        cursor.execute(
            """
            SELECT portfolio_id, user_id, headline, bio,
                   featured_projects, is_archived, created_at
            FROM Portfolios
            WHERE portfolio_id = %s
            """,
            (portfolio_id,),
        )
        portfolio = cursor.fetchone()

        if not portfolio:
            return jsonify({"error": "Portfolio not found"}), 404

        return jsonify(portfolio), 200

    except Exception:
        current_app.logger.exception("Error fetching portfolio")
        return jsonify({"error": "Failed to fetch portfolio"}), 500


@creator_bp.put("/portfolios/<int:portfolio_id>")
def update_portfolio(portfolio_id):
    """
    Update headline, bio, or featured projects.
    Matrix: PUT /portfolios/{portfolioID}
    """
    data = request.get_json(silent=True) or {}
    headline = data.get("headline")
    bio = data.get("bio")
    featured = data.get("featured_projects")

    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            UPDATE Portfolios
            SET headline = COALESCE(%s, headline),
                bio = COALESCE(%s, bio),
                featured_projects = COALESCE(%s, featured_projects)
            WHERE portfolio_id = %s
            """,
            (headline, bio, featured, portfolio_id),
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Portfolio not found"}), 404

        conn.commit()

        cursor.execute(
            """
            SELECT portfolio_id, user_id, headline, bio,
                   featured_projects, is_archived, created_at
            FROM Portfolios
            WHERE portfolio_id = %s
            """,
            (portfolio_id,),
        )
        return jsonify(cursor.fetchone()), 200

    except Exception:
        current_app.logger.exception("Error updating portfolio")
        return jsonify({"error": "Failed to update portfolio"}), 500


@creator_bp.delete("/portfolios/<int:portfolio_id>")
def archive_portfolio(portfolio_id):
    """
    Soft delete: hide portfolio from discovery.
    Matrix: DELETE /portfolios/{portfolioID}
    """
    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            "UPDATE Portfolios SET is_archived = TRUE WHERE portfolio_id = %s",
            (portfolio_id,),
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "Portfolio not found"}), 404

        conn.commit()
        return jsonify({"message": "Portfolio archived"}), 200

    except Exception:
        current_app.logger.exception("Error archiving portfolio")
        return jsonify({"error": "Failed to archive portfolio"}), 500


# PROJECTS
@creator_bp.get("/projects")
def list_projects():
    """
    Matrix: GET /projects
    """
    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            SELECT project_id, portfolio_id, title, description,
                   tags, visibility, is_archived, created_at
            FROM Projects
            WHERE is_archived = FALSE
            """
        )
        return jsonify({"projects": cursor.fetchall()}), 200

    except Exception:
        current_app.logger.exception("Error listing projects")
        return jsonify({"error": "Failed to list projects"}), 500


@creator_bp.post("/projects")
def create_project():
    """
    Matrix: POST /projects
    """
    data = request.get_json(silent=True) or {}

    portfolio_id = data.get("portfolio_id")
    title = data.get("title")
    description = data.get("description")
    tags = data.get("tags")

    if not portfolio_id or not title:
        return jsonify({"error": "Missing required fields: portfolio_id, title"}), 400

    try:
        conn, cursor = get_dict_cursor()
        cursor.execute(
            """
            INSERT INTO Projects (portfolio_id, title, description, tags)
            VALUES (%s, %s, %s, %s)
            """,
            (portfolio_id, title, description, tags),
        )
        project_id = cursor.lastrowid
        conn.commit()

        cursor.execute(
            """
            SELECT project_id, portfolio_id, title, description,
                   tags, visibility, is_archived, created_at
            FROM Projects
            WHERE project_id = %s
            """,
            (project_id,),
        )
        return jsonify(cursor.fetchone()), 201

    except Exception:
        current_app.logger.exception("Error creating project")
        return jsonify({"error": "Failed to create project"}), 500


@creator_bp.put("/projects")
def bulk_update_projects():
    """
    Matrix: PUT /projects – bulk update tags/metadata.
    Minimal school-friendly implementation:
    Request:
    { "tags": "updated, tags" }
    """
    data = request.get_json(silent=True) or {}
    new_tags = data.get("tags")

    if not new_tags:
        return jsonify({"error": "Nothing to update"}), 400

    try:
        conn, cursor = get_dict_cursor()
        cursor.execute(
            "UPDATE Projects SET tags = %s WHERE is_archived = FALSE",
            (new_tags,),
        )
        conn.commit()
        return jsonify({"message": "Projects updated"}), 200

    except Exception:
        current_app.logger.exception("Error bulk updating projects")
        return jsonify({"error": "Failed to bulk update"}), 500


# PROJECTS (singular)
@creator_bp.get("/projects/<int:project_id>")
def get_project(project_id):
    """
    Matrix: GET /projects/{projectID}
    """
    try:
        conn, cursor = get_dict_cursor()
        cursor.execute(
            """
            SELECT project_id, portfolio_id, title, description,
                   tags, visibility, is_archived, created_at
            FROM Projects
            WHERE project_id = %s
            """,
            (project_id,),
        )
        project = cursor.fetchone()

        if not project:
            return jsonify({"error": "Project not found"}), 404

        return jsonify(project), 200

    except Exception:
        current_app.logger.exception("Error retrieving project")
        return jsonify({"error": "Failed to retrieve project"}), 500


@creator_bp.put("/projects/<int:project_id>")
def update_project(project_id):
    """
    Update title, description, tags, visibility.
    Matrix: PUT /projects/{projectID}
    """
    data = request.get_json(silent=True) or {}

    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            UPDATE Projects
            SET title = COALESCE(%s, title),
                description = COALESCE(%s, description),
                tags = COALESCE(%s, tags),
                visibility = COALESCE(%s, visibility)
            WHERE project_id = %s
            """,
            (
                data.get("title"),
                data.get("description"),
                data.get("tags"),
                data.get("visibility"),
                project_id,
            ),
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Project not found"}), 404

        conn.commit()

        cursor.execute(
            """
            SELECT project_id, portfolio_id, title, description,
                   tags, visibility, is_archived, created_at
            FROM Projects
            WHERE project_id = %s
            """,
            (project_id,),
        )
        return jsonify(cursor.fetchone()), 200

    except Exception:
        current_app.logger.exception("Error updating project")
        return jsonify({"error": "Failed to update project"}), 500


@creator_bp.delete("/projects/<int:project_id>")
def delete_project(project_id):
    """
    Soft delete a project.
    Matrix: DELETE /projects/{projectID}
    """
    try:
        conn, cursor = get_dict_cursor()
        cursor.execute(
            "UPDATE Projects SET is_archived = TRUE WHERE project_id = %s",
            (project_id,),
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Project not found"}), 404

        return jsonify({"message": "Project archived"}), 200

    except Exception:
        current_app.logger.exception("Error deleting project")
        return jsonify({"error": "Failed to delete project"}), 500