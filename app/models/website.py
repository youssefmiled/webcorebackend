# app/models/website.py

from app.extensions import db
from datetime import datetime, timezone


class Website(db.Model):
    __tablename__ = "websites"

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(150), nullable=False)
    description   = db.Column(db.Text)
    template      = db.Column(db.String(50))
    primary_color = db.Column(db.String(20))
    logo          = db.Column(db.String(255))

    # ← NOUVEAU : stocke pages + blocks + globalStyles du CMS en JSON
    cms_data      = db.Column(db.JSON, nullable=True, default=None)

    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at    = db.Column(db.DateTime,
                              default=lambda: datetime.now(timezone.utc),
                              onupdate=lambda: datetime.now(timezone.utc))
    user_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Relations CMS avancé (tables Page/Block — cascade delete)
    pages = db.relationship(
        "Page",
        backref="website",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<Website {self.name}>"
