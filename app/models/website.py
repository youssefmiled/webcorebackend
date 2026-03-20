from app.extensions import db
from datetime import datetime

class Website(db.Model):
    __tablename__ = "websites"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    template = db.Column(db.String(50))
    primary_color = db.Column(db.String(20))
    logo = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<Website {self.name}>"