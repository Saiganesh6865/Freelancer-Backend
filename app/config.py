import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ---------- Environment ----------
    ENV = os.getenv("FLASK_ENV", "production")  # 'development' or 'production'
    DEBUG = ENV == "development"

    # ---------- Flask ----------
    SECRET_KEY = os.getenv("FLASK_SECRET", "super-secret-flask-key")

    # ---------- JWT (cookies) ----------
    JWT_TOKEN_LOCATION = ["cookies"]          # store JWT in cookies
    JWT_COOKIE_CSRF_PROTECT = True            # enable double-submit CSRF protection
    JWT_ACCESS_CSRF_HEADER_NAME = "X-CSRF-TOKEN"
    JWT_REFRESH_CSRF_HEADER_NAME = "X-CSRF-TOKEN"

    # ---------- Cookie flags ----------
    if ENV == "production":
        # Production: must use Secure + SameSite=None for cross-site cookies
        JWT_COOKIE_SECURE = True
        JWT_COOKIE_SAMESITE = "None"
    else:
        # Local development: simpler, no HTTPS required
        JWT_COOKIE_SECURE = False
        JWT_COOKIE_SAMESITE = "Lax"

    # ---------- Database ----------
    DB_USERNAME = os.getenv("DB_USERNAME", "user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "pass")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "db")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---------- CORS ----------
    # Include exact frontend URLs
    FRONTEND_ORIGINS = [
        "http://localhost:5173",
        "https://hanfreelancer.netlify.app",  # your production frontend
    ]
