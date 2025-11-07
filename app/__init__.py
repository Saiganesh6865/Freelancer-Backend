from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from .config import Config

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

    from app.controllers.job_invoice_controller import (
    freelancer_invoice_bp,
    manager_invoice_bp,
    admin_invoice_bp
    )

    app.register_blueprint(freelancer_invoice_bp)
    app.register_blueprint(manager_invoice_bp)
    app.register_blueprint(admin_invoice_bp)

    # ---------- Token revocation ----------
    with app.app_context():
        from app.models.revoked_token import RevokedToken

        @jwt.token_in_blocklist_loader
        def check_if_token_revoked(jwt_header, jwt_payload):
            """
            Checks if the JWT token is revoked.
            Automatically called by flask_jwt_extended.
            """
            jti = jwt_payload.get("jti")
            if not jti:
                return True  # invalid token considered revoked
            return RevokedToken.query.filter_by(jti=jti).first() is not None

        # Suppress Pylance unused warning
        _ = check_if_token_revoked

        # Optional: log revoked token attempts
        @jwt.revoked_token_loader
        def revoked_token_callback(jwt_header, jwt_payload):
            return {"error": "Token has been revoked"}, 401

        @jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            return {"error": "Token has expired"}, 401

        @jwt.invalid_token_loader
        def invalid_token_callback(error_string):
            return {"error": f"Invalid token: {error_string}"}, 422

        @jwt.unauthorized_loader
        def missing_token_callback(error_string):
            return {"error": f"Missing token: {error_string}"}, 401

    return app
