from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.repositories.user_repository import is_manager_request
from app.services.manager_service import (
    get_manager_dashboard_data,
    get_manager_jobs,
    get_manager_projects,
    get_manager_tasks,
    get_manager_batches,
    create_task_for_project,
    add_batch
)
from app.utils.response import error_response

bp = Blueprint("manager", __name__, url_prefix="/manager")

# ---------- Dashboard ----------
@bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    if not is_manager_request():
        return error_response("Only managers allowed", 403)
    manager_id = get_jwt_identity()
    data = get_manager_dashboard_data(manager_id)
    return jsonify(data), 200

# ---------- Jobs ----------
@bp.route("/jobs", methods=["GET"])
@jwt_required()
def jobs():
    if not is_manager_request():
        return error_response("Only managers allowed", 403)
    manager_id = get_jwt_identity()
    jobs = get_manager_jobs(manager_id)
    return jsonify(jobs), 200

# ---------- Projects ----------
@bp.route("/projects", methods=["GET"])
@jwt_required()
def projects():
    if not is_manager_request():
        return error_response("Only managers allowed", 403)
    manager_id = get_jwt_identity()
    projects = get_manager_projects(manager_id)
    return jsonify(projects), 200

# ---------- Tasks ----------
@bp.route("/tasks", methods=["GET"])
@jwt_required()
def tasks():
    if not is_manager_request():
        return error_response("Only managers allowed", 403)
    manager_id = get_jwt_identity()
    tasks = get_manager_tasks(manager_id)
    return jsonify(tasks), 200

@bp.route("/projects/<int:project_id>/tasks", methods=["POST"])
@jwt_required()
def create_task(project_id):
    claims = get_jwt()
    if claims.get("role") != "manager":
        return error_response("Managers only", 403)

    data = request.get_json()
    if not data:
        return error_response("Missing JSON body", 400)
    if not data.get("name"):
        return error_response("Task name is required", 400)
    if not data.get("batch_id"):
        return error_response("Batch ID is required", 400)

    try:
        task = create_task_for_project(get_jwt_identity(), project_id, data)
        return jsonify({"message": "Task created successfully", "task_id": task.id}), 200
    except ValueError as ve:
        return error_response(str(ve), 400)
    except Exception as e:
        print("Task creation error:", repr(e))
        return error_response("Internal server error", 500)

# ---------- Batches ----------
@bp.route("/batches", methods=["GET"])
@jwt_required()
def batches():
    if not is_manager_request():
        return error_response("Only managers allowed", 403)
    manager_id = get_jwt_identity()
    batches = get_manager_batches(manager_id)
    return jsonify(batches), 200

@bp.route("/batches", methods=["POST"])
@jwt_required()
def create_batch():
    if not is_manager_request():
        return error_response("Only managers allowed", 403)
    manager_id = get_jwt_identity()
    data = request.get_json()
    if not data or not data.get("project_id"):
        return error_response("Project ID is required", 400)
    try:
        batch = add_batch(manager_id, data)
        return jsonify({"message": "Batch created successfully", "batch_id": batch.id}), 200
    except ValueError as ve:
        return error_response(str(ve), 400)
    except Exception as e:
        print("Batch creation error:", repr(e))
        return error_response("Internal server error", 500)
