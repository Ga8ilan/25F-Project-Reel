from flask import Blueprint, jsonify, request 

social_bp = Blueprint("social", __name__)

#POSTS 

@social_bp.get("/posts")
def list_posts(): 
    """
    List posts in the feed (stub) 
    """
    # TODO: replace stub ith SQL query to fetch posts (w/ filters, ordering, etc)
    return jsonify({"message": "stub GET /posts"}), 200

@social_bp.post("/posts")
def create_post():
    """
    create a new post
    """
    # TODO: validate request body (required fileds, length, etc)
    # TODO: insert new post into Posts table 
    data = request.get_json(silent=False) or {}
    return jsonify({
        "message": "stub POST / posts",
        "received": data 
    }), 201

@social_bp.put("/posts/<int:post_id>")
def update_post(post_id):
    """
    Update an existing post
    """
    # TODO: validate payload
    # TODO: update existing post record in Posts table 
    data = request.get_json(silent=True) or {}
    return jsonify({
        "message": "stub PUT /posts/<id>",
        "post_id": post_id, 
        "updates": data
    }), 200

#MESSAGES 

@social_bp.get("/messages")
def list_messages():
    """
    List messages for current user 
    """
    # TODO: replace stub with DB query to fetch messages for authentication
    return jsonify({"message": "stub GET /messages"}), 200

@social_bp.post("/messages")
def create_message():
    """
    send a message
    """
    # TODO: validate request body 
    # TODO: insert nee message into Messages table and return new ID 
    data= request.get_json(silent=True) or {}
    return jsonify({
        "message": "stub POST /messages",
        "received": data 
    }), 201