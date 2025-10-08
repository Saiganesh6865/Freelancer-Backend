import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ---------- Flask ----------
    SECRET_KEY = os.getenv("FLASK_SECRET", "super-secret-flask-key")

    # ---------- JWT ----------
    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-jwt-key")
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = True          # HTTPS-only
    JWT_COOKIE_SAMESITE = "None"      # For cross-site cookies
    JWT_COOKIE_CSRF_PROTECT = True

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
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"sslmode": "require"},  # ensures Render SSL
        "pool_pre_ping": True                    # keeps idle connections alive
    }

    # ---------- CORS ----------
    FRONTEND_ORIGINS = [
        "http://localhost:5173",
        "https://hanfreelancer.netlify.app"
    ]
