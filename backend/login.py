from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from flask import current_app as app
import logging

login_bp = Blueprint('login', __name__)
logger = logging.getLogger(__name__)

@login_bp.route('/login', methods=['POST'])
def login():
    try:
        if not request.is_json:
            return jsonify({"success": False, "error": "Request must be JSON"}), 415
            
        data = request.get_json()
        email = data.get('email', '').lower()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({"success": False, "error": "Email and password required"}), 400

        # Check all collections
        user = None
        for collection_name in ['donor', 'institute', 'supplier']:
            user = app.db[collection_name].find_one({"email": email})
            if user:
                break

        if not user or not check_password_hash(user['password'], password):
            return jsonify({"success": False, "error": "Invalid credentials"}), 401

        # Create JWT token
        access_token = create_access_token(identity={
            "id": str(user["_id"]),
            "email": user["email"],
            "role": user.get("role", "user")
        })

        return jsonify({
            "success": True,
            "token": access_token,
            "user": {
                "id": str(user["_id"]),
                "name": user.get("name", ""),
                "email": user["email"],
                "role": user.get("role", "user")
            }
        }), 200

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"success": False, "error": "Login failed"}), 500