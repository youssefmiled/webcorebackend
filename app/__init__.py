import os
import logging
from flask import Flask, send_from_directory
from dotenv import load_dotenv
from flask_talisman import Talisman
from sqlalchemy import text

from .extensions import db, bcrypt, jwt, cors, mail, migrate, limiter
from .config import Config

logging.basicConfig(level=logging.DEBUG)


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── Mail ──────────────────────────────────────────────────────────────────
    app.config["MAIL_SERVER"]         = "smtp.gmail.com"
    app.config["MAIL_PORT"]           = 587
    app.config["MAIL_USE_TLS"]        = True
    app.config["MAIL_USE_SSL"]        = False
    app.config["MAIL_USERNAME"]       = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"]       = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

    # ── Upload folder ─────────────────────────────────────────────────────────
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ── DB + models (imports AVANT migrate) ───────────────────────────────────
    db.init_app(app)
    with app.app_context():
        from app.models.user import User
        from app.models.website import Website
        from app.models.activity_log import ActivityLog
        from app.models.page import Page
        from app.models.block import Block
        from app.models.media import Media          # ← NOUVEAU

    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # ── CORS ──────────────────────────────────────────────────────────────────
    cors.init_app(
        app,
        resources={r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ],
            "methods":       ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
            "supports_credentials": True,
        }},
    )

    mail.init_app(app)
    limiter.init_app(app)

    # ── Talisman ──────────────────────────────────────────────────────────────
    if os.getenv("FLASK_ENV") == "production":
        Talisman(app)
    else:
        Talisman(app, force_https=False, content_security_policy=None)

    # ── Routes internes ───────────────────────────────────────────────────────
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

    # ── Blueprints ────────────────────────────────────────────────────────────
    from .routes.auth import auth_bp
    from .routes.contact import contact_bp
    from .routes.website_routes import website_bp
    from .routes.upload import upload_bp
    from .routes.pages import pages_bp
    from .routes.blocks import blocks_bp
    from .routes.media import media_bp              # ← NOUVEAU

    app.register_blueprint(auth_bp,    url_prefix="/auth")
    app.register_blueprint(contact_bp, url_prefix="/contact")
    app.register_blueprint(website_bp)
    app.register_blueprint(upload_bp,  url_prefix="/api/upload")
    app.register_blueprint(pages_bp)
    app.register_blueprint(blocks_bp)
    app.register_blueprint(media_bp)               # ← NOUVEAU

    # ── Debug routes ──────────────────────────────────────────────────────────
    if os.getenv("FLASK_ENV") != "production":
        print("\n📋 Routes disponibles :")
        for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
            methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
            print(f"  [{methods:30s}] {rule.rule}")
        print()

    return app