# backend/app/routes/upload.py

import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

upload_bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "svg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 2MB

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route("", methods=["POST"])
def upload_file():
    if "logo" not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files["logo"]

    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"message": "File type not allowed. Use PNG, JPG, JPEG or SVG"}), 400

    # Check file size (Flask doesn't do it automatically)
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)
    if file_length > MAX_FILE_SIZE:
        return jsonify({"message": "File too large. Max 2MB"}), 400

    # Secure filename and generate unique name
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_filename)

    file.save(upload_path)

    # Build URL (adjust if you have a domain)
    file_url = f"/uploads/{unique_filename}"
    return jsonify({"url": file_url}), 200