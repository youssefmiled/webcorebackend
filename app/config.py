import os
from datetime import timedelta

class Config:
    # Connexion PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:1234@localhost:5432/cms_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")

    # JWT Token expiry
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)   # 24h en dev
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)   # 30 jours pour le refresh

    # Flask-Limiter — in-memory في dev، Redis في production
    RATELIMIT_STORAGE_URI = os.getenv("REDIS_URL", "memory://")