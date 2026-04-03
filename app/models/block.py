from datetime import datetime
from app import db


class Block(db.Model):
    __tablename__ = "blocks"

    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    type = db.Column(db.String(100), nullable=False)  # hero, navbar, features, footer, etc.
    order = db.Column(db.Integer, default=0, nullable=False)
    props = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "page_id": self.page_id,
            "type": self.type,
            "order": self.order,
            "props": self.props or {},
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self):
        return f"<Block {self.type} (page={self.page_id}, order={self.order})>" 
