# app/services/profile_service.py

import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

from app.extensions import db
from app.models.user import User
from app.models.user_settings import UserSettings

ALLOWED_EXT = {"png", "jpg", "jpeg", "webp", "gif"}
MAX_SIZE = 2 * 1024 * 1024   # 2 Mo


def _get_upload_folder() -> str:
    """Retourne le dossier d'upload configuré dans l'application Flask"""
    return current_app.config.get("UPLOAD_FOLDER", "uploads")


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def _save_avatar(file) -> str:
    upload_folder = _get_upload_folder()
    os.makedirs(upload_folder, exist_ok=True)
    timestamp = int(datetime.utcnow().timestamp())
    filename = f"{timestamp}_{secure_filename(file.filename)}"
    file.save(os.path.join(upload_folder, filename))
    # Retourne l'URL relative (sera servie par la route /uploads/<filename>)
    return f"/uploads/{filename}"


def _delete_avatar(path: str):
    if not path:
        return
    # path est de la forme "/uploads/nom_fichier"
    filename = os.path.basename(path)  # extrait le nom du fichier
    upload_folder = _get_upload_folder()
    disk_path = os.path.join(upload_folder, filename)
    if os.path.exists(disk_path):
        os.remove(disk_path)


def get_profile(user_id: int) -> dict:
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")

    s = UserSettings.query.filter_by(user_id=user_id).first()

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "phone": s.phone if s else "",
        "avatar": s.avatar if s else "",
    }


def update_profile(user_id: int, name: str, email: str, phone: str, file=None) -> dict:
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")

    name = (name or "").strip()
    email = (email or "").strip()
    phone = (phone or "").strip()

    if not name:
        raise ValueError("Name is required")
    if not email:
        raise ValueError("Email is required")

    # Vérifier unicité de l'email
    if email != user.email:
        if User.query.filter(User.email == email, User.id != user_id).first():
            raise ValueError("Email already used")
        user.email = email

    user.name = name

    # Settings (upsert)
    s = UserSettings.query.filter_by(user_id=user_id).first()
    if not s:
        s = UserSettings(user_id=user_id)
        db.session.add(s)

    # Mettre à jour le téléphone (permet de le vider)
    s.phone = phone if phone else None

    # Avatar
    if file and file.filename:
        if not _allowed(file.filename):
            raise ValueError("Invalid image format (png, jpg, jpeg, webp, gif)")
        file.seek(0, 2)
        if file.tell() > MAX_SIZE:
            raise ValueError("Image too large (max 2 MB)")
        file.seek(0)
        _delete_avatar(s.avatar)  # supprime l'ancien fichier
        s.avatar = _save_avatar(file)

    db.session.commit()

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "phone": s.phone or "",
        "avatar": s.avatar or "",
    }