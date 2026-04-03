from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.services.page_service import PageService
from app.utils.auth_helpers import get_current_user_id, get_owned_website, get_owned_page

# Import your Website model
from app.models.website import Website

pages_bp = Blueprint("pages", __name__, url_prefix="/api/pages")


@pages_bp.route("", methods=["POST"])
@jwt_required()
def create_page():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    website_id = data.get("website_id")
    if not website_id:
        return jsonify({"error": "website_id is required"}), 400

    website, err = get_owned_website(website_id)
    if err:
        return err

    required = ["title", "slug"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"'{field}' is required"}), 400

    try:
        page = PageService.create_page(website_id, data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 409

    return jsonify(page.to_dict()), 201


@pages_bp.route("", methods=["GET"])
@jwt_required()
def list_pages():
    website_id = request.args.get("website_id", type=int)
    if not website_id:
        return jsonify({"error": "website_id query param is required"}), 400

    website, err = get_owned_website(website_id)
    if err:
        return err

    pages = PageService.get_pages_by_website(website_id)
    return jsonify([p.to_dict() for p in pages]), 200


@pages_bp.route("/<int:page_id>", methods=["GET"])
@jwt_required()
def get_page(page_id):
    page, err = get_owned_page(page_id)
    if err:
        return err

    include_blocks = request.args.get("include_blocks", "false").lower() == "true"
    return jsonify(page.to_dict(include_blocks=include_blocks)), 200


@pages_bp.route("/<int:page_id>", methods=["PUT"])
@jwt_required()
def update_page(page_id):
    page, err = get_owned_page(page_id)
    if err:
        return err

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        page = PageService.update_page(page, data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 409

    return jsonify(page.to_dict()), 200


@pages_bp.route("/<int:page_id>", methods=["DELETE"])
@jwt_required()
def delete_page(page_id):
    page, err = get_owned_page(page_id)
    if err:
        return err

    PageService.delete_page(page)
    return jsonify({"message": "Page deleted"}), 200
