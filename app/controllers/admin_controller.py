from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.admin_service import (
    get_admin_stats,
    create_project,
    list_projects,
    update_project,
    delete_project,
    assign_manager_to_jobs,
    close_project
)
from app.utils.response import error_response

bp = Blueprint("admin", __name__, url_prefix="/admin")

UPLOAD_FOLDER = "uploads"

# ------------------- PROJECTS -------------------
@bp.route("/projects", methods=["POST"])
@jwt_required()
def create_project_route():
    """Admin-only route to create a new project."""
    claims = get_jwt()
    if claims.get("role") != "admin":
        return error_response("Admins only", 403)

    data = request.get_json()
    if not data:
        return error_response("Missing JSON body", 400)

    try:
        project = create_project(get_jwt_identity(), data)
        return jsonify({
            "message": "Project created successfully",
            "project_id": project.id
        }), 200
    except Exception as e:
        print("Project creation error:", e)
        return error_response(str(e), 400)


@bp.route("/projects", methods=["GET"])
@jwt_required()
def list_projects_route():
    """Admin-only route to list all projects."""
    claims = get_jwt()
    if claims.get("role") != "admin":
        return error_response("Admins only", 403)

    try:
        projects = list_projects()
        return jsonify(projects), 200
    except Exception as e:
        print("Project listing error:", e)
        return error_response(str(e), 400)


@bp.route("/projects/<int:project_id>", methods=["GET"])
@jwt_required()
def get_project_route(project_id):
    """Get a single project by ID"""
    claims = get_jwt()
    if claims.get("role") != "admin":
        return error_response("Admins only", 403)
    
    try:
        projects = list_projects()  # returns a list of dicts
        project = next((p for p in projects if p["id"] == project_id), None)
        if not project:
            return error_response("Project not found", 404)
        return jsonify(project), 200
    except Exception as e:
        print("Get project error:", e)
        return error_response(str(e), 400)


@bp.route("/projects/<int:project_id>", methods=["PUT"])
@jwt_required()
def update_project_route(project_id):
    """Admin-only route to update an existing project (supports optional file upload)."""
    claims = get_jwt()
    if claims.get("role") != "admin":
        return error_response("Admins only", 403)

    data = {}
    description_file = None

    try:
        # ✅ Handle both JSON and FormData
        if request.content_type and request.content_type.startswith("multipart/form-data"):
            data = request.form.to_dict()
            file = request.files.get("description_file")
            if file and file.filename:
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                data["description_file"] = file_path
        else:
            data = request.get_json() or {}

        if not data:
            return error_response("Missing data", 400)

        project = update_project(project_id, data)
        return jsonify({
            "success": True,
            "message": "Project updated successfully",
            "project_id": project.id
        }), 200

    except Exception as e:
        print("Project update error:", e)
        return error_response(str(e), 400)



@bp.route("/projects/<int:project_id>", methods=["DELETE"])
@jwt_required()
def delete_project_route(project_id):
    """Admin-only route to delete a project."""
    claims = get_jwt()
    if claims.get("role") != "admin":
        return error_response("Admins only", 403)

    try:
        delete_project(project_id)
        return jsonify({"message": "Project deleted successfully"}), 200
    except Exception as e:
        print("Project delete error:", e)
        return error_response(str(e), 400)


@bp.route("/assign-manager", methods=["POST"])
@jwt_required()
def assign_manager_route():
    """Admin-only route to assign a manager to multiple jobs."""
    claims = get_jwt()
    if claims.get("role") != "admin":
        return error_response("Admins only", 403)

    data = request.get_json()
    if not data:
        return error_response("Missing JSON body", 400)

    manager_username = data.get("manager_username")
    job_ids = data.get("job_ids")  # <-- expect a list here

    if not manager_username:
        return error_response("Missing manager_username", 400)
    if not job_ids or not isinstance(job_ids, list):
        return error_response("job_ids must be a non-empty list", 400)

    try:
        result, status_code = assign_manager_to_jobs(job_ids, manager_username)
        return jsonify(result), status_code
    except Exception as e:
        print("Assign manager error:", e)
        return error_response(str(e), 400)


@bp.route("/projects/<int:project_id>/close", methods=["PUT"])
@jwt_required()
def close_project_route(project_id):
    """Admin-only route to close project."""
    claims = get_jwt()
    if claims.get("role") != "admin":
        return error_response("Admins only", 403)

    try:
        project = close_project(project_id)
        return jsonify({"message": "Project closed", "project_id": project.id}), 200
    except Exception as e:
        print("Close project error:", e)
        return error_response(str(e), 400)


# ------------------- ADMIN STATS -------------------
@bp.route("/stats", methods=["GET"])
@jwt_required()
def stats():
    """Admin-only route to get system stats."""
    claims = get_jwt()
    if claims.get("role", "").lower() != "admin":
        return error_response("Unauthorized", 403)

    stats_data = get_admin_stats()
    return jsonify(stats_data), 200
