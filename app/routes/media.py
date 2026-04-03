from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin   # ← crucial
from app.services.media_service import MediaService

media_bp = Blueprint("media", __name__, url_prefix="/api/media")

def _current_user_id() -> int:
    return int(get_jwt_identity())

@media_bp.route("", methods=["POST"])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def upload_media():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400
    try:
        media = MediaService.upload(file, user_id=_current_user_id())
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    return jsonify(media.to_dict()), 201

@media_bp.route("", methods=["GET"])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def list_media():
    media_type = request.args.get("type", "all")
    items = MediaService.list_media(user_id=_current_user_id(), media_type=media_type)
    return jsonify([m.to_dict() for m in items]), 200

@media_bp.route("/<int:media_id>", methods=["DELETE"])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def delete_media(media_id):
    media = MediaService.get_by_id(media_id)
    if not media:
        return jsonify({"error": "Not found"}), 404
    if media.user_id != _current_user_id():
        return jsonify({"error": "Forbidden"}), 403
    MediaService.delete(media)
    return jsonify({"message": "Deleted"}), 200