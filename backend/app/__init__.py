from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS  # ✅ Import CORS
from .config import Config

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ✅ Enable CORS for frontend-backend integration
    CORS(app, supports_credentials=True, origins=["http://localhost:5173"])  # React dev server

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # ✅ Register blueprints
    from app.controllers import user_controller
    app.register_blueprint(user_controller.bp)

    from app.controllers import job_controller
    app.register_blueprint(job_controller.bp)

    from app.controllers import freelancer_controller
    app.register_blueprint(freelancer_controller.bp)

    from app.controllers import admin_controller
    app.register_blueprint(admin_controller.bp)

    from app.controllers.manager_controller import bp as manager_bp
    app.register_blueprint(manager_bp)
    

    with app.app_context():
        from app.models import user, revoked_token

        @jwt.token_in_blocklist_loader
        def check_if_token_revoked(jwt_header, jwt_payload):
            from app.models.revoked_token import RevokedToken
            jti = jwt_payload["jti"]
            return RevokedToken.query.filter_by(jti=jti).first() is not None

    return app
