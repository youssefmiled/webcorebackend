import os
import uuid
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask import current_app
from app.extensions import db
from app.models.media import Media

ALLOWED = {
    "image":    {"png", "jpg", "jpeg", "gif", "webp", "bmp", "tiff"},
    "svg":      {"svg"},
    "document": {"pdf", "doc", "docx"},
}
ALL_ALLOWED = {ext for exts in ALLOWED.values() for ext in exts}

def _detect_type(extension: str, mimetype: str) -> str:
    ext = extension.lower()
    if ext == "svg" or mimetype == "image/svg+xml":
        return "svg"
    if ext in ALLOWED["document"] or "pdf" in mimetype or "word" in mimetype or "officedocument" in mimetype:
        return "document"
    return "image"

def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"

class MediaService:

    @staticmethod
    def upload(file: FileStorage, user_id: int) -> Media:
        original_name = secure_filename(file.filename or "upload")
        extension = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
        if extension not in ALL_ALLOWED:
            raise ValueError(f"Extension '.{extension}' non autorisée.")

        unique_filename = f"{uuid.uuid4().hex}.{extension}"
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        save_path = os.path.join(upload_folder, unique_filename)
        file.save(save_path)
        size_bytes = os.path.getsize(save_path)

        media_type = _detect_type(extension, file.mimetype or "")
        media = Media(
            user_id   = user_id,
            name      = original_name,
            type      = media_type,
            extension = extension,
            size      = _format_size(size_bytes),
            filename  = unique_filename,
            url       = f"/uploads/{unique_filename}",
        )
        db.session.add(media)
        db.session.commit()
        return media

    @staticmethod
    def list_media(user_id: int, media_type: str | None = None):
        q = Media.query.filter_by(user_id=user_id)
        if media_type and media_type != "all":
            q = q.filter_by(type=media_type)
        return q.order_by(Media.created_at.desc()).all()

    @staticmethod
    def get_by_id(media_id: int) -> Media | None:
        return Media.query.get(media_id)

    @staticmethod
    def delete(media: Media) -> None:
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        file_path = os.path.join(upload_folder, media.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        db.session.delete(media)
        db.session.commit()