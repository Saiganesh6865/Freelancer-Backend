from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.admin_service import get_admin_stats
from app.utils.response import error_response
from app.services.admin_service import create_project_with_tasks

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/projects", methods=["POST"])
@jwt_required()
def create_project():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return error_response("Admins only", 403)

    data = request.get_json()
    if not data:
        return error_response("Missing JSON body", 400)

    try:
        project, error = create_project_with_tasks(get_jwt_identity(), data)
        if error:
            return error_response(error, 400)

        return jsonify({"message": "Project created successfully", "project_id": project.id}), 200
    except Exception as e:
        print("Project creation error:", e)
        return error_response("Internal server error", 500)




@bp.route("/stats", methods=["GET"])
@jwt_required()
def stats():
    identity = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role", "").lower()

    if role != "admin":
        return error_response("Unauthorized", 403)

    stats_data = get_admin_stats()
    return jsonify(stats_data)
