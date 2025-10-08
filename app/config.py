# app/config.py
import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Detect environment
    ENV = os.getenv("FLASK_ENV", "development")
    IS_PROD = ENV == "production"

    # ---------- Database ----------
    DB_USERNAME = os.getenv("DB_USERNAME", "postgres")
    DB_PASSWORD = urllib.parse.quote_plus(os.getenv("DB_PASSWORD", ""))
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "Han_Freelancer")

    # Add SSL for production (Render PostgreSQL)
    ssl_mode = "require" if IS_PROD else "disable"

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode={ssl_mode}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---------- Flask & JWT ----------
    FLASK_SECRET = os.getenv("FLASK_SECRET", "super-flask-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "super-jwt-secret")

    # JWT cookie settings
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_REFRESH_COOKIE_PATH = "/"
    JWT_COOKIE_SECURE = IS_PROD            # True in prod, False for local dev
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_COOKIE_CSRF_PROTECT = False        # Can enable later if needed
