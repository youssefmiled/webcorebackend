from flask import Blueprint, request, jsonify
from app.services.website_service import WebsiteService
from app.schemas.website_schema import website_schema, websites_schema


website_bp = Blueprint("websites", __name__, url_prefix="/api/websites")


@website_bp.route("", methods=["POST"])
def create_website():

    data = request.json

    if not data.get("name"):
        return jsonify({"message": "Name is required"}), 400

    website = WebsiteService.create_website(data)

    return jsonify({
        "message": "Website created successfully",
        "website": website_schema.dump(website)
    }), 201


@website_bp.route("", methods=["GET"])
def get_websites():

    websites = WebsiteService.get_all_websites()

    return jsonify(websites_schema.dump(websites))


@website_bp.route("/<int:website_id>", methods=["GET"])
def get_website(website_id):

    website = WebsiteService.get_website_by_id(website_id)

    if not website:
        return jsonify({"message": "Website not found"}), 404

    return jsonify(website_schema.dump(website))


@website_bp.route("/<int:website_id>", methods=["PUT"])
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
def delete_website(website_id):

    website = WebsiteService.delete_website(website_id)

    if not website:
        return jsonify({"message": "Website not found"}), 404

    return jsonify({"message": "Website deleted successfully"})