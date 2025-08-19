from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.admin_service import (
    get_admin_stats,
    create_project,
    list_projects,
    update_project,
    delete_project,
    assign_manager,
    close_project
)
from app.utils.response import error_response

bp = Blueprint("admin", __name__, url_prefix="/admin")

# ------------------- PROJECTS -------------------
@bp.route("/projects", methods=["POST"])
@jwt_required()
def create_project_route():
    """
    Admin-only route to create a new project.
    """
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
        }), 201
    except Exception as e:
        print("Project creation error:", e)
        return error_response(str(e), 400)


@bp.route("/projects", methods=["GET"])
@jwt_required()
def list_projects_route():
    """
    Admin-only route to list all projects.
    """
    claims = get_jwt()
    if claims.get("role") != "admin":
        return error_response("Admins only", 403)

    try:
        projects = list_projects()
        return jsonify(projects), 200
    except Exception as e:
        print("Project listing error:", e)
        return error_response(str(e), 400)


@bp.route("/projects/<int:project_id>", methods=["PUT"])
@jwt_required()
def update_project_route(project_id):
    """
    Admin-only route to update an existing project.
    """
    claims = get_jwt()
    if claims.get("role") != "admin":
        return error_response("Admins only", 403)

    data = request.get_json()
    if not data:
        return error_response("Missing JSON body", 400)

    try:
        project = update_project(project_id, data)
        return jsonify({
            "message": "Project updated successfully",
            "project_id": project.id
        }), 200
    except Exception as e:
        print("Project update error:", e)
        return error_response(str(e), 400)


@bp.route("/projects/<int:project_id>", methods=["DELETE"])
@jwt_required()
def delete_project_route(project_id):
    """
    Admin-only route to delete a project.
    """
    claims = get_jwt()
    if claims.get("role") != "admin":
        return error_response("Admins only", 403)

    try:
        delete_project(project_id)
        return jsonify({"message": "Project deleted successfully"}), 200
    except Exception as e:
        print("Project delete error:", e)
        return error_response(str(e), 400)



@bp.route("/projects/<int:project_id>/assign-manager", methods=["PUT"])
@jwt_required()
def assign_manager_route(project_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return error_response("Admins only", 403)

    manager_id = request.args.get("manager_id")
    if not manager_id:
        return error_response("Missing manager_id", 400)

    try:
        project = assign_manager(project_id, manager_id)
        return jsonify({"message": "Manager assigned", "project_id": project.id}), 200
    except Exception as e:
        print("Assign manager error:", e)
        return error_response(str(e), 400)

@bp.route("/projects/<int:project_id>/close", methods=["PUT"])
@jwt_required()
def close_project_route(project_id):
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
    """
    Admin-only route to get system stats.
    """
    claims = get_jwt()
    if claims.get("role", "").lower() != "admin":
        return error_response("Unauthorized", 403)

    stats_data = get_admin_stats()
    return jsonify(stats_data), 200
