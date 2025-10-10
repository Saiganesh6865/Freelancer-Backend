from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
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

    # ✅ Ensures Flask detects HTTPS correctly behind reverse proxy (e.g., Render, Nginx)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    # ✅ CORS setup for cross-site cookies
    CORS(
        app,
        supports_credentials=True,
        origins=Config.FRONTEND_ORIGINS,
    )

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # ---------- Register Blueprints ----------
    from app.controllers.user_controller import bp as user_controller
    from app.controllers.job_controller import bp as job_controller
    from app.controllers.freelancer_controller import bp as freelancer_controller
    from app.controllers.admin_controller import bp as admin_controller
    try:
        from app.controllers.manager_controller import bp as manager_bp
    except Exception:
        manager_bp = None

    app.register_blueprint(user_controller)
    app.register_blueprint(job_controller)
    app.register_blueprint(freelancer_controller)
    app.register_blueprint(admin_controller)
    if manager_bp:
        app.register_blueprint(manager_bp)

    # ---------- JWT Token Revocation ----------
    with app.app_context():
        from app.models.revoked_token import RevokedToken

        @jwt.token_in_blocklist_loader
        def check_if_token_revoked(jwt_header, jwt_payload):
            jti = jwt_payload["jti"]
            return RevokedToken.query.filter_by(jti=jti).first() is not None

    return app

