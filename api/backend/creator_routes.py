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
    
# USERS & CREATORS

@creator_bp.get("/users")
def list_users():
    """
    Matrix: GET /creator/users
    List active users in the system.
    """
    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            SELECT
                user_id,
                name,
                email,
                role,
                location,
                primary_styles,
                tools,
                headline,
                bio,
                socials,
                is_creator,
                market,
                credit_momentum,
                is_active,
                created_at
            FROM Users
            WHERE is_active = TRUE
            """
        )
        users = cursor.fetchall()
        return jsonify({"users": users}), 200

    except Exception:
        current_app.logger.exception("Error listing users")
        return jsonify({"error": "Failed to list users"}), 500


@creator_bp.get("/users/<int:user_id>")
def get_user(user_id):
    """
    Matrix: GET /creator/users/{userID}
    """
    try:
        conn, cursor = get_dict_cursor()
        cursor.execute(
            """
            SELECT
                user_id,
                name,
                email,
                role,
                location,
                primary_styles,
                tools,
                headline,
                bio,
                socials,
                is_creator,
                market,
                credit_momentum,
                is_active,
                created_at
            FROM Users
            WHERE user_id = %s
            """,
            (user_id,),
        )
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify(user), 200

    except Exception:
        current_app.logger.exception("Error fetching user")
        return jsonify({"error": "Failed to fetch user"}), 500


@creator_bp.put("/users/<int:user_id>")
def update_user(user_id):
    """
    Matrix: PUT /creator/users/{userID}
    Simple profile update (headline/bio/location/tools/etc.).
    """
    data = request.get_json(silent=True) or {}

    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            UPDATE Users
            SET
                name            = COALESCE(%s, name),
                role            = COALESCE(%s, role),
                location        = COALESCE(%s, location),
                primary_styles  = COALESCE(%s, primary_styles),
                tools           = COALESCE(%s, tools),
                headline        = COALESCE(%s, headline),
                bio             = COALESCE(%s, bio),
                socials         = COALESCE(%s, socials),
                market          = COALESCE(%s, market)
            WHERE user_id = %s
            """,
            (
                data.get("name"),
                data.get("role"),
                data.get("location"),
                data.get("primary_styles"),
                data.get("tools"),
                data.get("headline"),
                data.get("bio"),
                data.get("socials"),
                data.get("market"),
                user_id,
            ),
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "User not found"}), 404

        conn.commit()

        cursor.execute(
            """
            SELECT
                user_id,
                name,
                email,
                role,
                location,
                primary_styles,
                tools,
                headline,
                bio,
                socials,
                is_creator,
                market,
                credit_momentum,
                is_active,
                created_at
            FROM Users
            WHERE user_id = %s
            """,
            (user_id,),
        )
        return jsonify(cursor.fetchone()), 200

    except Exception:
        current_app.logger.exception("Error updating user")
        return jsonify({"error": "Failed to update user"}), 500


@creator_bp.delete("/users/<int:user_id>")
def deactivate_user(user_id):
    """
    Matrix: DELETE /creator/users/{userID}
    Soft-delete: mark user as inactive.
    """
    try:
        conn, cursor = get_dict_cursor()
        cursor.execute(
            "UPDATE Users SET is_active = FALSE WHERE user_id = %s",
            (user_id,),
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "User not found"}), 404

        conn.commit()
        return jsonify({"message": "User deactivated"}), 200

    except Exception:
        current_app.logger.exception("Error deactivating user")
        return jsonify({"error": "Failed to deactivate user"}), 500


@creator_bp.get("/creators")
def list_creators():
    """
    Matrix: GET /creator/creators
    Convenience view filtered to creator accounts.
    """
    try:
        conn, cursor = get_dict_cursor()
        cursor.execute(
            """
            SELECT
                user_id,
                name,
                email,
                role,
                location,
                primary_styles,
                tools,
                headline,
                bio,
                socials,
                is_creator,
                market,
                credit_momentum,
                is_active,
                created_at
            FROM Users
            WHERE is_creator = TRUE
              AND is_active = TRUE
            """
        )
        creators = cursor.fetchall()
        return jsonify({"creators": creators}), 200

    except Exception:
        current_app.logger.exception("Error listing creators")
        return jsonify({"error": "Failed to list creators"}), 500
    
# COLLABORATIONS (ProjectCredits)

@creator_bp.get("/collaborations")
def list_collaborations():
    """
    Matrix: GET /creator/collaborations
    Simple collaboration directory based on ProjectCredits.
    Optional filter: ?user_id=#
    """
    user_id = request.args.get("user_id")

    try:
        conn, cursor = get_dict_cursor()

        if user_id:
            cursor.execute(
                """
                SELECT
                    credit_id,
                    project_id,
                    user_id,
                    role,
                    verified,
                    created_at
                FROM ProjectCredits
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
        else:
            cursor.execute(
                """
                SELECT
                    credit_id,
                    project_id,
                    user_id,
                    role,
                    verified,
                    created_at
                FROM ProjectCredits
                ORDER BY created_at DESC
                """
            )

        return jsonify({"collaborations": cursor.fetchall()}), 200

    except Exception:
        current_app.logger.exception("Error listing collaborations")
        return jsonify({"error": "Failed to list collaborations"}), 500


@creator_bp.post("/collaborations")
def create_collaboration():
    """
    Matrix: POST /creator/collaborations
    Create a standalone credit record.
    """
    data = request.get_json(silent=True) or {}
    project_id = data.get("project_id")
    user_id = data.get("user_id")
    role = data.get("role")
    verified = data.get("verified", False)

    if not (project_id and user_id):
        return jsonify({"error": "Missing required fields: project_id, user_id"}), 400

    try:
        conn, cursor = get_dict_cursor()
        cursor.execute(
            """
            INSERT INTO ProjectCredits (project_id, user_id, role, verified)
            VALUES (%s, %s, %s, %s)
            """,
            (project_id, user_id, role, verified),
        )
        credit_id = cursor.lastrowid
        conn.commit()

        cursor.execute(
            """
            SELECT
                credit_id,
                project_id,
                user_id,
                role,
                verified,
                created_at
            FROM ProjectCredits
            WHERE credit_id = %s
            """,
            (credit_id,),
        )
        return jsonify(cursor.fetchone()), 201

    except Exception:
        current_app.logger.exception("Error creating collaboration")
        return jsonify({"error": "Failed to create collaboration"}), 500


@creator_bp.put("/collaborations/<int:credit_id>")
def update_collaboration(credit_id):
    """
    Matrix: PUT /creator/collaborations/{creditID}
    Update role/verified on a collaboration.
    """
    data = request.get_json(silent=True) or {}
    role = data.get("role")
    verified = data.get("verified")

    if role is None and verified is None:
        return jsonify({"error": "Nothing to update"}), 400

    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            UPDATE ProjectCredits
            SET
                role = COALESCE(%s, role),
                verified = COALESCE(%s, verified)
            WHERE credit_id = %s
            """,
            (role, verified, credit_id),
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Collaboration not found"}), 404

        conn.commit()

        cursor.execute(
            """
            SELECT
                credit_id,
                project_id,
                user_id,
                role,
                verified,
                created_at
            FROM ProjectCredits
            WHERE credit_id = %s
            """,
            (credit_id,),
        )
        return jsonify(cursor.fetchone()), 200

    except Exception:
        current_app.logger.exception("Error updating collaboration")
        return jsonify({"error": "Failed to update collaboration"}), 500


@creator_bp.delete("/collaborations/<int:credit_id>")
def delete_collaboration(credit_id):
    """
    Matrix: DELETE /creator/collaborations/{creditID}
    Simple hard delete.
    """
    try:
        conn, cursor = get_dict_cursor()
        cursor.execute(
            "DELETE FROM ProjectCredits WHERE credit_id = %s",
            (credit_id,),
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Collaboration not found"}), 404

        conn.commit()
        return jsonify({"message": "Collaboration deleted"}), 200

    except Exception:
        current_app.logger.exception("Error deleting collaboration")
        return jsonify({"error": "Failed to delete collaboration"}), 500
    
# PROJECT CREDITS NESTED

@creator_bp.get("/projects/<int:project_id>/credits")
def list_project_credits(project_id):
    """
    Matrix: GET /creator/projects/{projectID}/credits
    """
    try:
        conn, cursor = get_dict_cursor()
        cursor.execute(
            """
            SELECT
                credit_id,
                project_id,
                user_id,
                role,
                verified,
                created_at
            FROM ProjectCredits
            WHERE project_id = %s
            ORDER BY created_at DESC
            """,
            (project_id,),
        )
        return jsonify({"credits": cursor.fetchall()}), 200

    except Exception:
        current_app.logger.exception("Error listing project credits")
        return jsonify({"error": "Failed to list project credits"}), 500


@creator_bp.post("/projects/<int:project_id>/credits")
def add_project_credit(project_id):
    """
    Matrix: POST /creator/projects/{projectID}/credits
    """
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    role = data.get("role")
    verified = data.get("verified", False)

    if not user_id:
        return jsonify({"error": "Missing required field: user_id"}), 400

    try:
        conn, cursor = get_dict_cursor()
        cursor.execute(
            """
            INSERT INTO ProjectCredits (project_id, user_id, role, verified)
            VALUES (%s, %s, %s, %s)
            """,
            (project_id, user_id, role, verified),
        )
        credit_id = cursor.lastrowid
        conn.commit()

        cursor.execute(
            """
            SELECT
                credit_id,
                project_id,
                user_id,
                role,
                verified,
                created_at
            FROM ProjectCredits
            WHERE credit_id = %s
            """,
            (credit_id,),
        )
        return jsonify(cursor.fetchone()), 201

    except Exception:
        current_app.logger.exception("Error adding project credit")
        return jsonify({"error": "Failed to add project credit"}), 500


@creator_bp.put("/projects/<int:project_id>/credits/<int:credit_id>")
def update_project_credit(project_id, credit_id):
    """
    Matrix: PUT /creator/projects/{projectID}/credits/{creditID}
    """
    data = request.get_json(silent=True) or {}
    role = data.get("role")
    verified = data.get("verified")

    if role is None and verified is None:
        return jsonify({"error": "Nothing to update"}), 400

    try:
        conn, cursor = get_dict_cursor()
        cursor.execute(
            """
            UPDATE ProjectCredits
            SET
                role = COALESCE(%s, role),
                verified = COALESCE(%s, verified)
            WHERE credit_id = %s
              AND project_id = %s
            """,
            (role, verified, credit_id, project_id),
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Credit not found for this project"}), 404

        conn.commit()

        cursor.execute(
            """
            SELECT
                credit_id,
                project_id,
                user_id,
                role,
                verified,
                created_at
            FROM ProjectCredits
            WHERE credit_id = %s
            """,
            (credit_id,),
        )
        return jsonify(cursor.fetchone()), 200

    except Exception:
        current_app.logger.exception("Error updating project credit")
        return jsonify({"error": "Failed to update project credit"}), 500


@creator_bp.delete("/projects/<int:project_id>/credits/<int:credit_id>")
def delete_project_credit(project_id, credit_id):
    """
    Matrix: DELETE /creator/projects/{projectID}/credits/{creditID}
    """
    try:
        conn, cursor = get_dict_cursor()
        cursor.execute(
            """
            DELETE FROM ProjectCredits
            WHERE credit_id = %s
              AND project_id = %s
            """,
            (credit_id, project_id),
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Credit not found for this project"}), 404

        conn.commit()
        return jsonify({"message": "Project credit deleted"}), 200

    except Exception:
        current_app.logger.exception("Error deleting project credit")
        return jsonify({"error": "Failed to delete project credit"}), 500


# PROJECT MEDIA

@creator_bp.get("/projects/<int:project_id>/media")
def list_project_media(project_id):
    """
    Matrix: GET /creator/projects/{projectID}/media
    """
    try:
        conn, cursor = get_dict_cursor()
        cursor.execute(
            """
            SELECT
                media_id,
                project_id,
                media_url,
                media_type,
                caption,
                alt_text,
                sort_order,
                created_at
            FROM ProjectMedia
            WHERE project_id = %s
            ORDER BY sort_order ASC, created_at ASC
            """,
            (project_id,),
        )
        return jsonify({"media": cursor.fetchall()}), 200

    except Exception:
        current_app.logger.exception("Error listing project media")
        return jsonify({"error": "Failed to list media"}), 500


@creator_bp.post("/projects/<int:project_id>/media")
def add_project_media(project_id):
    """
    Matrix: POST /creator/projects/{projectID}/media
    """
    data = request.get_json(silent=True) or {}
    media_url = data.get("media_url")
    media_type = data.get("media_type")
    caption = data.get("caption")
    alt_text = data.get("alt_text")
    sort_order = data.get("sort_order", 0)

    if not media_url:
        return jsonify({"error": "Missing required field: media_url"}), 400

    try:
        conn, cursor = get_dict_cursor()
        cursor.execute(
            """
            INSERT INTO ProjectMedia (
                project_id, media_url, media_type,
                caption, alt_text, sort_order
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (project_id, media_url, media_type, caption, alt_text, sort_order),
        )
        media_id = cursor.lastrowid
        conn.commit()

        cursor.execute(
            """
            SELECT
                media_id,
                project_id,
                media_url,
                media_type,
                caption,
                alt_text,
                sort_order,
                created_at
            FROM ProjectMedia
            WHERE media_id = %s
            """,
            (media_id,),
        )
        return jsonify(cursor.fetchone()), 201

    except Exception:
        current_app.logger.exception("Error adding project media")
        return jsonify({"error": "Failed to add media"}), 500


@creator_bp.put("/projects/<int:project_id>/media")
def bulk_update_project_media(project_id):
    """
    Matrix: PUT /creator/projects/{projectID}/media
    Simple bulk update for sort order or captions.
    Request body example:
    {
      "items": [
        {"media_id": 1, "sort_order": 1},
        {"media_id": 2, "sort_order": 2}
      ]
    }
    """
    data = request.get_json(silent=True) or {}
    items = data.get("items")

    if not items:
        return jsonify({"error": "Nothing to update"}), 400

    try:
        conn, cursor = get_dict_cursor()

        for item in items:
            media_id = item.get("media_id")
            sort_order = item.get("sort_order")
            caption = item.get("caption")
            alt_text = item.get("alt_text")

            if not media_id:
                continue

            updates = []
            params = []

            if sort_order is not None:
                updates.append("sort_order = %s")
                params.append(sort_order)
            if caption is not None:
                updates.append("caption = %s")
                params.append(caption)
            if alt_text is not None:
                updates.append("alt_text = %s")
                params.append(alt_text)

            if not updates:
                continue

            params.extend([media_id, project_id])

            cursor.execute(
                f"""
                UPDATE ProjectMedia
                SET {", ".join(updates)}
                WHERE media_id = %s
                  AND project_id = %s
                """,
                params,
            )

        conn.commit()
        return jsonify({"message": "Media updated"}), 200

    except Exception:
        current_app.logger.exception("Error bulk updating media")
        return jsonify({"error": "Failed to update media"}), 500


@creator_bp.delete("/projects/<int:project_id>/media/<int:media_id>")
def delete_project_media(project_id, media_id):
    """
    Matrix: DELETE /creator/projects/{projectID}/media/{mediaID}
    """
    try:
        conn, cursor = get_dict_cursor()
        cursor.execute(
            """
            DELETE FROM ProjectMedia
            WHERE media_id = %s
              AND project_id = %s
            """,
            (media_id, project_id),
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Media not found for this project"}), 404

        conn.commit()
        return jsonify({"message": "Media deleted"}), 200

    except Exception:
        current_app.logger.exception("Error deleting media")
        return jsonify({"error": "Failed to delete media"}), 500