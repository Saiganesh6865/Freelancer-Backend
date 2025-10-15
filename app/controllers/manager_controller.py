from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.manager_service import (
    get_manager_dashboard_data,
    get_manager_jobs,
    get_manager_tasks,
    create_task_for_job,
    add_batch,
    get_batch_applications,
    change_application_status,
    get_manager_freelancers,
    change_task_status,
    get_manager_batches
)
from app.repositories.user_repository import is_manager_request
from app.repositories.batch_repository import get_batch_members
from app.utils.response import error_response

bp = Blueprint("manager", __name__, url_prefix="/manager")


# ---------- Helpers ----------
def require_manager():
    return is_manager_request()


def manager_id():
    return get_jwt_identity()


# ---------- Dashboard ----------
@bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    if not require_manager():
        return error_response("Managers only", 403)
    try:
        data = get_manager_dashboard_data(manager_id())
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        print("Dashboard error:", repr(e))
        return error_response("Internal server error", 500)


# ---------- Projects ----------
@bp.route("/projects", methods=["GET"])
@jwt_required()
def projects():
    if not require_manager():
        return error_response("Managers only", 403)
    try:
        data = get_manager_jobs(manager_id())
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        print("Projects listing error:", repr(e))
        return error_response("Internal server error", 500)


# ---------- Tasks ----------
@bp.route("/tasks", methods=["POST"])
@jwt_required()
def get_tasks():
    if not require_manager():
        return error_response("Managers only", 403)

    data = request.get_json() or {}
    project_id = data.get("job_id")
    if not project_id:
        return error_response("job_id is required", 400)

    try:
        tasks = get_manager_tasks(manager_id(), job_id=project_id)
        return jsonify({"status": "success", "data": tasks}), 200
    except Exception as e:
        print("Manager tasks error:", repr(e))
        return error_response("Internal server error", 500)


@bp.route("/assign_tasks", methods=["POST"])
@jwt_required()
def create_task():
    if not require_manager():
        return error_response("Managers only", 403)

    data = request.get_json() or {}

    # Required fields: title, batch_id (assigned_to_username is optional)
    required_fields = ["title", "batch_id"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}", 400)

    try:
        # task creation will use batch_id to find job_id internally if needed
        task = create_task_for_job(manager_id(), data)
        return jsonify({"status": "success", "data": task}), 200
    except ValueError as ve:
        return error_response(str(ve), 400)
    except Exception as e:
        print("Task creation error:", repr(e))
        return error_response("Internal server error", 500)


@bp.route("/tasks/status", methods=["PATCH"])
@jwt_required()
def update_task_status_manager():
    if not require_manager():
        return error_response("Managers only", 403)

    data = request.get_json() or {}
    task_id = data.get("task_id")
    status = data.get("status")

    if not task_id or not status:
        return error_response("task_id and status are required", 400)

    try:
        task = change_task_status(manager_id(), task_id, status)
        return jsonify({"status": "success", "message": "Task status updated", "data": task}), 200
    except ValueError as ve:
        return error_response(str(ve), 404)
    except Exception as e:
        print("Manager task status update error:", repr(e))
        return error_response("Internal server error", 500)


# ---------- Batches ----------
@bp.route("/batches", methods=["GET"])
@jwt_required()
def batches():
    if not require_manager():
        return error_response("Managers only", 403)
    try:
        data = get_manager_batches(manager_id())
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        print("Batches listing error:", repr(e))
        return error_response("Internal server error", 500)


@bp.route("/batches", methods=["POST"])
@jwt_required()
def create_batch():
    if not require_manager():
        return error_response("Managers only", 403)

    data = request.get_json() or {}
    if not data.get("project_id"):
        return error_response("project_id is required", 400)

    try:
        batch = add_batch(manager_id(), data)
        return jsonify({"status": "success", "message": "Batch created successfully", "data": batch}), 200
    except ValueError as ve:
        return error_response(str(ve), 400)
    except Exception as e:
        print("Batch creation error:", repr(e))
        return error_response("Internal server error", 500)


# ---------- Freelancers ----------
@bp.route("/freelancers", methods=["GET"])
@jwt_required()
def freelancers():
    if not require_manager():
        return error_response("Managers only", 403)

    try:
        data = get_manager_freelancers(manager_id())
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        print("Freelancers listing error:", repr(e))
        return error_response("Internal server error", 500)


# ---------- Applications ----------
@bp.route("/batches/applications", methods=["POST"])
@jwt_required()
def list_batch_applications():
    if not require_manager():
        return error_response("Managers only", 403)

    data = request.get_json() or {}
    batch_id = data.get("batch_id")
    if not batch_id:
        return error_response("batch_id is required", 400)

    try:
        applications = get_batch_applications(manager_id(), batch_id)
        return jsonify({"status": "success", "data": applications}), 200
    except Exception as e:
        print("Applications listing error:", repr(e))
        return error_response("Internal server error", 500)


@bp.route("/batch_applications/status", methods=["PATCH"])
@jwt_required()
def update_application_status_route():
    if not require_manager():
        return error_response("Managers only", 403)

    data = request.get_json() or {}
    application_id = data.get("application_id")
    status = data.get("status")

    if not application_id:
        return error_response("application_id is required", 400)
    if status not in ["accepted", "rejected"]:
        return error_response("Invalid status", 400)

    try:
        updated = change_application_status(application_id, status)
        if not updated:
            return error_response("Application not found", 404)
        return jsonify({"status": "success", "message": "Application updated", "data": updated}), 200
    except Exception as e:
        print("Application status update error:", repr(e))
        return error_response("Internal server error", 500)


# ---------- Batch Members ----------
@bp.route("/batch_members_list", methods=["POST"])
@jwt_required()
def batch_members():
    if not require_manager():
        return error_response("Managers only", 403)

    data = request.json
    batch_id = data.get("batch_id")
    project_id = data.get("project_id")

    if not batch_id:
        return error_response("batch_id is required", 400)
    if not project_id:
        return error_response("project_id is required", 400)

    try:
        result = get_batch_members(batch_id)
        return jsonify({
            "status": "success",
            "batch_id": batch_id,
            "project_id": project_id,
            "members": result.get("team_members", [])
        }), 200
    except Exception as e:
        return error_response(str(e), 500)


from app.repositories.batch_repository import assign_freelancers_to_batch
from app.auth.auth_utils import get_current_manager_id

@bp.route("/assign-freelancer-to-project", methods=["POST"])
@jwt_required()  # ensure JWT is present
def assign_freelancer_to_project():
    data = request.get_json()
    batch_id = data.get("batch_id")
    freelancer_ids = data.get("freelancer_ids", [])

    manager_id = get_current_manager_id()  # from JWT now

    result = assign_freelancers_to_batch(manager_id, batch_id, freelancer_ids)

    return jsonify(result)
