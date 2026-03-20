from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.website_service import WebsiteService
from app.schemas.website_schema import website_schema, websites_schema

website_bp = Blueprint("websites", __name__, url_prefix="/api/websites")

@website_bp.route("", methods=["POST"])
@jwt_required()   # ✅ يلزم توكن
def create_website():
    user_id = get_jwt_identity()   # ✅ من التوكن مش من البودي
    data = request.json

    if not data.get("name"):
        return jsonify({"message": "Name is required"}), 400

    data["user_id"] = user_id
    website = WebsiteService.create_website(data)

    return jsonify({
        "message": "Website created successfully",
        "website": website_schema.dump(website)
    }), 201

@website_bp.route("", methods=["GET"])
@jwt_required()
def get_websites():
    page = request.args.get("page", 1, type=int)
    result = WebsiteService.get_all_websites(page=page)
    return jsonify({
        "websites": websites_schema.dump(result.items),
        "total": result.total,
        "pages": result.pages,
        "current_page": result.page
    })

@website_bp.route("/<int:website_id>", methods=["GET"])
@jwt_required()
def get_website(website_id):
    website = WebsiteService.get_website_by_id(website_id)
    if not website:
        return jsonify({"message": "Website not found"}), 404
    return jsonify(website_schema.dump(website))

@website_bp.route("/<int:website_id>", methods=["PUT"])
@jwt_required()
def update_website(website_id):
    data = request.json
    website = WebsiteService.update_website(website_id, data)
    if not website:
        return jsonify({"message": "Website not found"}), 404
    return jsonify({
        "message": "Website updated successfully",
        "website": website_schema.dump(website)
    })

@website_bp.route("/<int:website_id>", methods=["DELETE"])
@jwt_required()
def delete_website(website_id):
    website = WebsiteService.delete_website(website_id)
    if not website:
        return jsonify({"message": "Website not found"}), 404
    return jsonify({"message": "Website deleted successfully"})