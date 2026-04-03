# app/models/activity_log.py

from app.extensions import db
from datetime import datetime, timezone


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action     = db.Column(db.String(20), nullable=False)   # CREATE | UPDATE | DELETE
    item_name  = db.Column(db.String(255), nullable=False)
    website_id = db.Column(db.Integer, nullable=True)
    details    = db.Column(db.Text, nullable=True)           # ← NOUVEAU
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        return {
            "id":         self.id,
            "action":     self.action,
            "item":       self.item_name,
            "website_id": self.website_id,
            "details":    self.details,                      # ← NOUVEAU
            "date":       self.created_at.isoformat(),
        }