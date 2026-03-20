from datetime import datetime
from app.extensions import db, bcrypt

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(150), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), default='user')

    is_two_fa_enabled = db.Column(db.Boolean, default=False)

    two_fa_code = db.Column(db.String(6), nullable=True)

    two_fa_code_expiration = db.Column(db.DateTime, nullable=True)

    reset_code = db.Column(db.String(6), nullable=True)

    reset_code_expiration = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    def set_password(self,password):

        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")


    def check_password(self,password):

        return bcrypt.check_password_hash(self.password_hash,password)