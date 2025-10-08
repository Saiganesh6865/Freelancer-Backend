import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

class Config:
    ENV = os.getenv("FLASK_ENV", "development")
    IS_PROD = ENV == "production"

    # ---------- Database ----------
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = urllib.parse.quote_plus(os.getenv("DB_PASSWORD"))
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")

    # SQLAlchemy URI
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Force SSL on production
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"sslmode": "require"} if IS_PROD else {}
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---------- Flask & JWT ----------
    FLASK_SECRET = os.getenv("FLASK_SECRET")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET")

    # JWT cookie settings
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_REFRESH_COOKIE_PATH = "/"
    JWT_COOKIE_SECURE = IS_PROD
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_COOKIE_CSRF_PROTECT = False
