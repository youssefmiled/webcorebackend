# app/models/userSettings.py

from app.extensions import db
from datetime import datetime


class UserSettings(db.Model):
    __tablename__ = "user_settings"

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    phone  = db.Column(db.String(30),  nullable=True)
    avatar = db.Column(db.String(255), nullable=True)   # ex: /uploads/1234_photo.jpg

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship(
        "User",
        backref=db.backref("settings", uselist=False, cascade="all, delete-orphan"),
    )

    def to_dict(self):
        return {
            "id":         self.id,
            "user_id":    self.user_id,
            "phone":      self.phone  or "",
            "avatar":     self.avatar or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }