from app.extensions import db
from datetime import datetime, timezone

class Media(db.Model):
    __tablename__ = "media"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name       = db.Column(db.String(255), nullable=False)
    type       = db.Column(db.String(20),  nullable=False)   # image | svg | document
    extension  = db.Column(db.String(20),  nullable=False)
    size       = db.Column(db.String(30),  nullable=False)
    filename   = db.Column(db.String(255), nullable=False)   # nom unique sur disque
    url        = db.Column(db.String(500), nullable=False)   # /uploads/...
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        # Formatage compatible Windows : remplace " 0" par " " pour supprimer le zéro initial
        date_str = self.created_at.strftime("%b %d, %Y").replace(" 0", " ")
        return {
            "id":        self.id,
            "name":      self.name,
            "type":      self.type,
            "extension": self.extension,
            "size":      self.size,
            "fileUrl":   self.url,
            "date":      date_str,
        }

    def __repr__(self):
        return f"<Media {self.name} ({self.type})>"