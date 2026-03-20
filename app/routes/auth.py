from flask import Blueprint, request, jsonify, current_app
from app.models.user import User
from app.extensions import db, mail
from flask_jwt_extended import create_access_token
from flask_mail import Message
from datetime import datetime, timedelta
import random
import re

auth_bp = Blueprint("auth", __name__)

password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}$'

def generate_code():
    return str(random.randint(100000, 999999))

def email_template(title, message, code):
    return f"""
    <html>
    <body style="margin:0;padding:0;background:#f4f6fb;font-family:Arial">
    <table width="100%"><tr><td align="center">
    <table width="500" style="background:white;border-radius:12px;padding:30px;margin-top:40px">
    <tr><td align="center">
    <h2>{title}</h2>
    <p>{message}</p>
    <div style="margin:30px 0;font-size:32px;letter-spacing:6px;font-weight:bold;color:#2563eb;">
    {code}
    </div>
    <p style="font-size:13px">This code will expire in a few minutes.</p>
    <hr>
    <p style="font-size:12px">© 2026 WebCore Platform</p>
    </td></tr>
    </table>
    </td></tr></table>
    </body>
    </html>
    """

def send_email(subject, recipient, html):
    msg = Message(
        subject=subject,
        recipients=[recipient],
        sender=current_app.config["MAIL_DEFAULT_SENDER"]
    )
    msg.html = html
    mail.send(msg)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"message": "All fields required"}), 400
    if not re.match(password_regex, password):
        return jsonify({"message": "Password not strong enough"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    user = User(name=name, email=email, role="user", is_two_fa_enabled=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    if user.is_two_fa_enabled:
        code = generate_code()
        user.two_fa_code = code
        user.two_fa_code_expiration = datetime.utcnow() + timedelta(minutes=5)
        db.session.commit()

        html = email_template("Your 2FA Code", "Use this code to complete login", code)
        send_email("2FA Code", user.email, html)

        return jsonify({
            "two_fa_required": True,
            "email": user.email,
            "role": user.role
        }), 200

    access_token = create_access_token(identity=user.id)
    return jsonify({
        "access_token": access_token,
        "role": user.role,
        "name": user.name,
        "email": user.email
    }), 200

# ✅ EL FIX — ma3adch y7tej token, w yraje3 name + email
@auth_bp.route("/2fa", methods=["POST"])
def verify_2fa():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    if user.two_fa_code != code:
        return jsonify({"message": "Invalid code"}), 401
    if datetime.utcnow() > user.two_fa_code_expiration:
        return jsonify({"message": "Code expired"}), 401

    user.two_fa_code = None
    user.two_fa_code_expiration = None
    db.session.commit()

    token = create_access_token(identity=user.id)
    return jsonify({
        "access_token": token,
        "role": user.role,
        "name": user.name,      # ✅ zidha
        "email": user.email     # ✅ zidha
    }), 200

@auth_bp.route("/resend-2fa", methods=["POST"])
def resend_2fa():
    data = request.get_json()
    email = data.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    code = generate_code()
    user.two_fa_code = code
    user.two_fa_code_expiration = datetime.utcnow() + timedelta(minutes=5)
    db.session.commit()

    html = email_template("New 2FA Code", "Use this new code", code)
    send_email("New 2FA Code", email, html)

    return jsonify({"message": "New code sent"}), 200

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    code = generate_code()
    user.reset_code = code
    user.reset_code_expiration = datetime.utcnow() + timedelta(minutes=10)
    db.session.commit()

    html = email_template("Reset Password", "Use this code to reset your password", code)
    send_email("Password Reset Code", email, html)

    return jsonify({"message": "Reset code sent"}), 200

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    if user.reset_code != code:
        return jsonify({"message": "Invalid reset code"}), 400
    if datetime.utcnow() > user.reset_code_expiration:
        return jsonify({"message": "Code expired"}), 400
    if not re.match(password_regex, password):
        return jsonify({"message": "Password not strong enough"}), 400

    user.set_password(password)
    user.reset_code = None
    user.reset_code_expiration = None
    db.session.commit()

    return jsonify({"message": "Password reset successful"}), 200