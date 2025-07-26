from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app import app
from datetime import datetime
from bson import ObjectId
import re
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

register_bp = Blueprint('register', __name__)
logger = logging.getLogger(__name__)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))

def validate_password(password: str) -> bool:
    return len(password) >= 8 and any(c.isupper() for c in password) and any(c.isdigit() for c in password)

@register_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Request must be JSON"
            }), 415
            
        data = request.get_json()
        
        # Validation
        required_fields = {
            "all": ["email", "password", "role"],
            "institute": ["name", "location", "registrationYear"],
            "donor": ["name", "location"],
            "supplier": ["name", "location", "storeType"]
        }
        
        role = data["role"].lower()
        if role not in required_fields:
            return jsonify({
                "success": False,
                "error": f"Invalid role: {role}"
            }), 400
        
        missing_fields = [f for f in required_fields["all"] + required_fields[role] if f not in data]
        if missing_fields:
            return jsonify({
                "success": False,
                "error": "Missing fields",
                "missing": missing_fields
            }), 400
            
        if not validate_email(data["email"]):
            return jsonify({
                "success": False,
                "error": "Invalid email"
            }), 400
            
        if not validate_password(data["password"]):
            return jsonify({
                "success": False,
                "error": "Password must be 8+ chars with uppercase and number"
            }), 400
        
        # Check for duplicate email
        for col in ['donor', 'institute', 'supplier']:
            if app.db[col].find_one({"email": data["email"].lower()}):
                return jsonify({
                    "success": False,
                    "error": "Email already exists"
                }), 409
        
        # Prepare document
        user_data = {
            "_id": ObjectId(),
            "name": data.get("name", "").strip(),
            "email": data["email"].lower().strip(),
            "password": generate_password_hash(data["password"]),
            "location": data.get("location", "").strip(),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "isActive": True,
            "role": role
        }
        
        if role == "institute":
            try:
                user_data["registrationYear"] = datetime.strptime(data["registrationYear"], '%Y-%m-%d')
                user_data["verificationStatus"] = "pending"
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "Invalid date format (YYYY-MM-DD)"
                }), 400
        elif role == "supplier":
            user_data["storeType"] = data.get("storeType", "").strip()
        
        # Insert to appropriate collection
        result = app.db[role].insert_one(user_data)
        
        if not result.acknowledged:
            raise Exception("Insert not acknowledged")
        
        return jsonify({
            "success": True,
            "message": "Registration successful",
            "user": {
                "id": str(user_data["_id"]),
                "name": user_data["name"],
                "email": user_data["email"],
                "role": role,
                "createdAt": user_data["createdAt"].isoformat()
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Registration failed",
            "details": str(e)
        }), 500