from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from .config import Config

# ---------- Extensions ----------
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---------- CORS ----------
    CORS(
        app,
        supports_credentials=True,
        origins=Config.FRONTEND_ORIGINS
    )

    # ---------- Init extensions ----------
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # ---------- Blueprints ----------
    from app.controllers import (
        user_controller,
        job_controller,
        freelancer_controller,
        admin_controller
    )
    from app.controllers.manager_controller import bp as manager_bp

    app.register_blueprint(user_controller.bp)
    app.register_blueprint(job_controller.bp)
    app.register_blueprint(freelancer_controller.bp)
    app.register_blueprint(admin_controller.bp)
    app.register_blueprint(manager_bp)

    # ---------- JWT Token Revocation ----------
    with app.app_context():
        from app.models.revoked_token import RevokedToken

        @jwt.token_in_blocklist_loader
        def check_if_token_revoked(jwt_header, jwt_payload):
            jti = jwt_payload["jti"]
            return RevokedToken.query.filter_by(jti=jti).first() is not None

    return app
