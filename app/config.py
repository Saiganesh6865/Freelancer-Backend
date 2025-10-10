import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ENV = os.getenv("FLASK_ENV", "development")  # development / production
    SECRET_KEY = os.getenv("FLASK_SECRET", "super-secret-flask-key")

    # ---------- JWT ----------
    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-jwt-key")
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ACCESS_CSRF_HEADER_NAME = "X-CSRF-TOKEN"

    if ENV == "development":
        JWT_COOKIE_SECURE = False
        JWT_COOKIE_SAMESITE = "Lax"
    else:
        JWT_COOKIE_SECURE = True
        JWT_COOKIE_SAMESITE = "None"

    # ---------- Database ----------
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", 5432)
    DB_NAME = os.getenv("DB_NAME")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"sslmode": "require"}, "pool_pre_ping": True}

    # ---------- Frontend ----------
    FRONTEND_ORIGINS = [
        "http://localhost:5173",
        "https://hanfreelancer.netlify.app"
    ]
