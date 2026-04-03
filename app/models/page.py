from datetime import datetime
from app import db


class Page(db.Model):
    __tablename__ = "pages"

    id = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey("websites.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, default=0, nullable=False)
    is_home = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    blocks = db.relationship(
        "Block",
        backref="page",
        cascade="all, delete-orphan",
        order_by="Block.order",
        lazy="select",
    )

    # Unique slug per website
    __table_args__ = (
        db.UniqueConstraint("website_id", "slug", name="uq_page_slug_per_website"),
    )

    def to_dict(self, include_blocks=False):
        data = {
            "id": self.id,
            "website_id": self.website_id,
            "title": self.title,
            "slug": self.slug,
            "order": self.order,
            "is_home": self.is_home,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        if include_blocks:
            data["blocks"] = [b.to_dict() for b in self.blocks.order_by("order")]
        return data

    def __repr__(self):
        return f"<Page {self.slug} (website={self.website_id})>"
