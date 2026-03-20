# backend/app/__init__.py
import os
import logging
from flask import Flask, request, send_from_directory
from dotenv import load_dotenv
from flask_talisman import Talisman
from sqlalchemy import text

from .extensions import db, bcrypt, jwt, cors, mail, migrate, limiter
from .config import Config

from .routes.auth import auth_bp
from .routes.contact import contact_bp
from .routes.website_routes import website_bp
from .routes.upload import upload_bp

logging.basicConfig(level=logging.DEBUG)

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)

    # -----------------------
    # MAIL CONFIG
    # -----------------------
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

    # -----------------------
    # UPLOAD FOLDER
    # -----------------------
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # -----------------------
    # INITIALIZE EXTENSIONS
    # -----------------------
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    Talisman(app)

    # -----------------------
    # ROUTES
    # -----------------------
    @app.route("/test-db")
    def test_db():
        try:
            db.session.execute(text("SELECT 1"))
            return "Database connected!"
        except Exception as e:
            return str(e)

    @app.route("/")
    @limiter.limit("50 per hour")
    def home():
        return "Backend OK"

    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # -----------------------
    # REGISTER BLUEPRINTS
    # -----------------------
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(contact_bp, url_prefix="/contact")
    app.register_blueprint(website_bp, url_prefix="/api/websites")
    app.register_blueprint(upload_bp, url_prefix="/api/upload")

    print("Routes Flask disponibles :")
    for rule in app.url_map.iter_rules():
        print(rule)

    return app