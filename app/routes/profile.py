from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.profile_service import get_profile, update_profile

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/", methods=["GET"])
@jwt_required()
def get_profile_route():
    user_id = get_jwt_identity()
    # Convertir en entier si c'est une chaîne numérique
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)
    
    try:
        user = get_profile(user_id)
        return jsonify({"success": True, "user": user})
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"GET profile error: {e}")
        return jsonify({"success": False, "message": "Server error"}), 500

@profile_bp.route("/", methods=["PUT"])
@jwt_required()
def update_profile_route():
    user_id = get_jwt_identity()
    # Convertir en entier si c'est une chaîne numérique
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)
    
    name = request.form.get("name", "")
    email = request.form.get("email", "")
    phone = request.form.get("phone", "")
    file = request.files.get("avatar")
    
    try:
        updated = update_profile(user_id, name, email, phone, file)
        return jsonify({"success": True, "message": "Profile updated successfully", "user": updated})
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"PUT profile error: {e}")
        return jsonify({"success": False, "message": "Server error"}), 500