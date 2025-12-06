from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import db

social_bp = Blueprint("social", __name__)


#DB connection
def get_dict_cursor():
    conn = db.get_db()
    cursor = conn.cursor()
    return conn, cursor


# POSTS

@social_bp.get("/posts")
def list_posts():
    """
    Return a feed of posts with optional filters.
    REST Matrix: GET /posts
    """
    try:
        conn, cursor = get_dict_cursor()

        user_id = request.args.get("userID") #optional filter
        visibility = request.args.get("visibility")   # optional filter

        conditions = ["is_deleted = FALSE"]
        params = []

        if user_id:
            conditions.append("user_id = %s")
            params.append(user_id)

        if visibility:
            conditions.append("visibility = %s")
            params.append(visibility)

        where_clause = " AND ".join(conditions)

        cursor.execute(
            f"""
            SELECT
                post_id,
                user_id,
                media_url,
                caption,
                tags,
                visibility,
                created_at
            FROM Posts
            WHERE {where_clause}
            ORDER BY created_at DESC
            """,
            params,
        )
        posts = cursor.fetchall()
        return jsonify({"posts": posts}), 200

    except Exception:
        current_app.logger.exception("Error fetching posts")
        return jsonify({"error": "Failed to fetch posts"}), 500



@social_bp.post("/posts")
def create_post():
    """
    Create a new post (media optional).
    REST Matrix: POST /posts
    """
    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    caption = data.get("caption")
    media_url = data.get("media_url")       #optional
    visibility = data.get("visibility", "public")
    tags = data.get("tags", None)

    if not user_id:
        return jsonify({"error": "Missing required field: user_id"}), 400

    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            INSERT INTO Posts (
                user_id, media_url, caption, tags, visibility
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, media_url, caption, tags, visibility),
        )

        post_id = cursor.lastrowid
        conn.commit()

        cursor.execute(
            """
            SELECT
                post_id, user_id, media_url, caption,
                tags, visibility, created_at
            FROM Posts
            WHERE post_id = %s
            """,
            (post_id,),
        )
        new_post = cursor.fetchone()

        return jsonify(new_post), 201

    except Exception:
        current_app.logger.exception("Error creating post")
        return jsonify({"error": "Failed to create post"}), 500



@social_bp.put("/posts/<int:post_id>")
def update_post(post_id):
    """
    Edit a post’s caption, tags, or visibility.
    REST Matrix: PUT /posts/{postID}
    """
    data = request.get_json(silent=True) or {}

    caption = data.get("caption")
    tags = data.get("tags")
    visibility = data.get("visibility")

    try:
        conn, cursor = get_dict_cursor()

        updates = []
        params = []

        if caption is not None:
            updates.append("caption = %s")
            params.append(caption)

        if tags is not None:
            updates.append("tags = %s")
            params.append(tags)

        if visibility is not None:
            updates.append("visibility = %s")
            params.append(visibility)

        if not updates:
            return jsonify({"error": "Nothing to update"}), 400

        params.append(post_id)

        cursor.execute(
            f"""
            UPDATE Posts
            SET {", ".join(updates)}
            WHERE post_id = %s AND is_deleted = FALSE
            """,
            params,
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Post not found"}), 404

        conn.commit()

        cursor.execute(
            """
            SELECT
                post_id, user_id, media_url, caption,
                tags, visibility, created_at
            FROM Posts
            WHERE post_id = %s
            """,
            (post_id,),
        )
        updated = cursor.fetchone()

        return jsonify(updated), 200

    except Exception:
        current_app.logger.exception("Error updating post")
        return jsonify({"error": "Failed to update post"}), 500



@social_bp.delete("/posts/<int:post_id>")
def delete_post(post_id):
    """
    Soft-delete a post.
    REST Matrix: DELETE /posts/{postID}
    """
    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            UPDATE Posts
            SET is_deleted = TRUE
            WHERE post_id = %s
            """,
            (post_id,),
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Post not found"}), 404

        conn.commit()

        return jsonify({"message": "Post removed", "post_id": post_id}), 200

    except Exception:
        current_app.logger.exception("Error deleting post")
        return jsonify({"error": "Failed to delete post"}), 500



# POST INTERACTIONS

@social_bp.get("/post-interactions")
def list_post_interactions():
    """
    Return views/likes/comments for a post.
    REST Matrix: GET /post-interactions
    """
    post_id = request.args.get("postID")

    if not post_id:
        return jsonify({"error": "Missing required query parameter: postID"}), 400

    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            SELECT
                interaction_id,
                post_id,
                user_id,
                interaction_type,
                comment_text,
                created_at
            FROM PostInteractions
            WHERE post_id = %s
            ORDER BY created_at DESC
            """,
            (post_id,),
        )
        interactions = cursor.fetchall()

        return jsonify({"interactions": interactions}), 200

    except Exception:
        current_app.logger.exception("Error fetching interactions")
        return jsonify({"error": "Failed to fetch interactions"}), 500



@social_bp.post("/post-interactions")
def create_post_interaction():
    """
    Record a view/like/comment on a post.
    REST Matrix: POST /post-interactions
    """
    data = request.get_json(silent=True) or {}

    post_id = data.get("post_id")
    user_id = data.get("user_id")
    interaction_type = data.get("interaction_type")
    comment_text = data.get("comment_text")

    if not (post_id and user_id and interaction_type):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            INSERT INTO PostInteractions (
                post_id, user_id, interaction_type, comment_text
            )
            VALUES (%s, %s, %s, %s)
            """,
            (post_id, user_id, interaction_type, comment_text),
        )

        interaction_id = cursor.lastrowid
        conn.commit()

        cursor.execute(
            """
            SELECT
                interaction_id,
                post_id,
                user_id,
                interaction_type,
                comment_text,
                created_at
            FROM PostInteractions
            WHERE interaction_id = %s
            """,
            (interaction_id,),
        )
        new_row = cursor.fetchone()

        return jsonify(new_row), 201

    except Exception:
        current_app.logger.exception("Error creating interaction")
        return jsonify({"error": "Failed to record interaction"}), 500



@social_bp.delete("/post-interactions/<int:interaction_id>")
def delete_post_interaction(interaction_id):
    """
    Remove/anonymize an interaction.
    REST Matrix: DELETE /post-interactions/{interactionID}
    """
    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            UPDATE PostInteractions
            SET user_id = NULL,
                comment_text = NULL
            WHERE interaction_id = %s
            """,
            (interaction_id,),
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Interaction not found"}), 404

        conn.commit()

        return jsonify({"message": "Interaction anonymized"}), 200

    except Exception:
        current_app.logger.exception("Error anonymizing interaction")
        return jsonify({"error": "Failed to anonymize interaction"}), 500



# MESSAGES

@social_bp.get("/messages")
def list_messages():
    """
    List message threads for a user.
    REST Matrix: GET /messages
    """
    user_id = request.args.get("userID")

    if not user_id:
        return jsonify({"error": "Missing required query parameter: userID"}), 400

    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            SELECT
                message_id,
                sender_id,
                receiver_id,
                content,
                is_read,
                is_starred,
                is_archived,
                created_at
            FROM Messages
            WHERE
                (sender_id = %s AND is_deleted_by_sender = FALSE)
                OR
                (receiver_id = %s AND is_deleted_by_receiver = FALSE)
            ORDER BY created_at DESC
            """,
            (user_id, user_id),
        )
        messages = cursor.fetchall()

        return jsonify({"messages": messages}), 200

    except Exception:
        current_app.logger.exception("Error fetching messages")
        return jsonify({"error": "Failed to fetch messages"}), 500



@social_bp.post("/messages")
def create_message():
    """
    Send a new message or reply.
    REST Matrix: POST /messages
    """
    data = request.get_json(silent=True) or {}

    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    content = data.get("content")

    if not (sender_id and receiver_id and content):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn, cursor = get_dict_cursor()

        cursor.execute(
            """
            INSERT INTO Messages (
                sender_id, receiver_id, content
            )
            VALUES (%s, %s, %s)
            """,
            (sender_id, receiver_id, content),
        )

        message_id = cursor.lastrowid
        conn.commit()

        cursor.execute(
            """
            SELECT
                message_id,
                sender_id,
                receiver_id,
                content,
                is_read,
                is_starred,
                is_archived,
                created_at
            FROM Messages
            WHERE message_id = %s
            """,
            (message_id,),
        )
        new_msg = cursor.fetchone()

        return jsonify(new_msg), 201

    except Exception:
        current_app.logger.exception("Error creating message")
        return jsonify({"error": "Failed to create message"}), 500



@social_bp.put("/messages/<int:message_id>")
def update_message(message_id):
    """
    Update message metadata (mark read, archive, star).
    REST Matrix: PUT /messages/{messageID}
    """
    data = request.get_json(silent=True) or {}

    is_read = data.get("is_read")
    is_starred = data.get("is_starred")
    is_archived = data.get("is_archived")

    try:
        conn, cursor = get_dict_cursor()

        updates = []
        params = []

        if is_read is not None:
            updates.append("is_read = %s")
            params.append(is_read)

        if is_starred is not None:
            updates.append("is_starred = %s")
            params.append(is_starred)

        if is_archived is not None:
            updates.append("is_archived = %s")
            params.append(is_archived)

        if not updates:
            return jsonify({"error": "Nothing to update"}), 400

        params.append(message_id)

        cursor.execute(
            f"""
            UPDATE Messages
            SET {", ".join(updates)}
            WHERE message_id = %s
            """,
            params,
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Message not found"}), 404

        conn.commit()

        cursor.execute(
            """
            SELECT
                message_id,
                sender_id,
                receiver_id,
                content,
                is_read,
                is_starred,
                is_archived,
                created_at
            FROM Messages
            WHERE message_id = %s
            """,
            (message_id,),
        )
        updated = cursor.fetchone()

        return jsonify(updated), 200

    except Exception:
        current_app.logger.exception("Error updating message")
        return jsonify({"error": "Failed to update message"}), 500



@social_bp.delete("/messages/<int:message_id>")
def delete_message(message_id):
    """
    Soft-delete a message for a specific user.
    REST Matrix: DELETE /messages/{messageID}
    """
    user_id = request.args.get("userID")

    if not user_id:
        return jsonify({"error": "Missing userID for delete"}), 400

    try:
        conn, cursor = get_dict_cursor()

        # Determine whether user is sender or receiver
        cursor.execute(
            """
            SELECT sender_id, receiver_id
            FROM Messages
            WHERE message_id = %s
            """,
            (message_id,),
        )
        msg = cursor.fetchone()

        if not msg:
            return jsonify({"error": "Message not found"}), 404

        sender_id = msg["sender_id"]
        receiver_id = msg["receiver_id"]

        if str(user_id) == str(sender_id):
            cursor.execute(
                "UPDATE Messages SET is_deleted_by_sender = TRUE WHERE message_id = %s",
                (message_id,),
            )
        elif str(user_id) == str(receiver_id):
            cursor.execute(
                "UPDATE Messages SET is_deleted_by_receiver = TRUE WHERE message_id = %s",
                (message_id,),
            )
        else:
            return jsonify({"error": "User does not have permission to delete this message"}), 403

        conn.commit()

        return jsonify({"message": "Message hidden", "message_id": message_id}), 200

    except Exception:
        current_app.logger.exception("Error deleting message")
        return jsonify({"error": "Failed to hide message"}), 500