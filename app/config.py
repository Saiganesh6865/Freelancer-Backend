# app/config.py
import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_USERNAME = os.getenv("DB_USERNAME", "freelancer_mzep_user")
    DB_PASSWORD = urllib.parse.quote_plus(os.getenv("DB_PASSWORD", "2c88XV73Llj3gLtEDpzunHaPMSPs5riD"))
    DB_HOST = os.getenv("DB_HOST", "dpg-d2esisuuk2gs73bq9jp0-a.oregon-postgres.render.com")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "freelancer_mzep")

    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FLASK_SECRET = os.getenv("FLASK_SECRET", "super-flask-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "super-jwt-secret")


        # --- JWT Cookie settings for dev ---
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_REFRESH_COOKIE_PATH = "/"       # Send refresh cookie on all backend paths
    JWT_COOKIE_SECURE = False           # HTTP for dev, HTTPS in production
    JWT_COOKIE_SAMESITE = "Lax"         # Works with HTTP localhost, allows cookies on same-site requests
    JWT_COOKIE_CSRF_PROTECT = False     # Optional, disable for now
