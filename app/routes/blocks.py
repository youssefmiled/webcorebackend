from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.services.block_service import BlockService
from app.utils.auth_helpers import get_current_user_id, get_owned_page, get_owned_block

# Import your Website model
from app.models.website import Website
from app.models.page import Page

blocks_bp = Blueprint("blocks", __name__, url_prefix="/api/blocks")


@blocks_bp.route("", methods=["POST"])
@jwt_required()
def create_block():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    page_id = data.get("page_id")
    if not page_id:
        return jsonify({"error": "page_id is required"}), 400

    page, err = get_owned_page(page_id)
    if err:
        return err

    if not data.get("type"):
        return jsonify({"error": "'type' is required"}), 400

    block = BlockService.create_block(page_id, data)
    return jsonify(block.to_dict()), 201


@blocks_bp.route("", methods=["GET"])
@jwt_required()
def list_blocks():
    page_id = request.args.get("page_id", type=int)
    if not page_id:
        return jsonify({"error": "page_id query param is required"}), 400

    page, err = get_owned_page(page_id)
    if err:
        return err

    blocks = BlockService.get_blocks_by_page(page_id)
    return jsonify([b.to_dict() for b in blocks]), 200


@blocks_bp.route("/<int:block_id>", methods=["PUT"])
@jwt_required()
def update_block(block_id):
    block, err = get_owned_block(block_id)
    if err:
        return err

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    block = BlockService.update_block(block, data)
    return jsonify(block.to_dict()), 200


@blocks_bp.route("/<int:block_id>", methods=["DELETE"])
@jwt_required()
def delete_block(block_id):
    block, err = get_owned_block(block_id)
    if err:
        return err

    BlockService.delete_block(block)
    return jsonify({"message": "Block deleted"}), 200


@blocks_bp.route("/reorder", methods=["PATCH"])
@jwt_required()
def reorder_blocks():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    page_id = data.get("page_id")
    ordered_ids = data.get("ordered_ids")  # e.g. [3, 1, 2]

    if not page_id or not isinstance(ordered_ids, list):
        return jsonify({"error": "page_id and ordered_ids (list) are required"}), 400

    page, err = get_owned_page(page_id)
    if err:
        return err

    try:
        blocks = BlockService.reorder_blocks(page_id, ordered_ids)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify([b.to_dict() for b in blocks]), 200
