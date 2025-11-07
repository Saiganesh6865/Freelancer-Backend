from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app.services.manager_service import (
    get_manager_dashboard_data,
    get_manager_jobs,
    get_manager_tasks,
    add_batch,
    get_batch_applications,
    change_application_status,
    get_manager_freelancers,
    change_task_status,
    edit_batch
)
from app.repositories.user_repository import is_manager_request
from app.repositories.batch_repository import get_batches_by_manager, get_batch_members, assign_freelancers_to_batch
from app.repositories.task_repository import create_task
from app.auth.auth_utils import get_current_manager_id
from app.utils.response import success_response, error_response
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.models.BatchMember import BatchMember
from sqlalchemy.orm import joinedload
from app.models.job import Job
from app.models.batch import Batch
from app.models.task import Task
import json
from app.services.task_service import edit_task


bp = Blueprint("manager", __name__, url_prefix="/manager")


# ---------- Secure Wrapper ----------
def secure_jwt_required(fn):
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()  # ✅ Ensures CSRF token is valid
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return jwt_required()(wrapper)


# ---------- Helpers ----------
def require_manager():
    return is_manager_request()

def manager_id():
    """
    Return the JWT identity as an integer when possible.
    This avoids string/int mismatches when comparing to DB ids.
    """
    identity = get_jwt_identity()
    try:
        return int(identity)
    except (TypeError, ValueError):
        return identity



# ---------- Dashboard ----------
@bp.route("/dashboard", methods=["GET"])
@secure_jwt_required
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
@secure_jwt_required
def projects():
    if not require_manager():
        return error_response("Managers only", 403)
    try:
        data = get_manager_jobs(manager_id())
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        print("Projects listing error:", repr(e))
        return error_response("Internal server error", 500)


# ---------- Single Project ----------
@bp.route("/projects/<int:project_id>", methods=["GET"])
@secure_jwt_required
def get_full_project(project_id):
    if not require_manager():
        return error_response("Managers only", 403)
    
    try:
        manager = manager_id()
        project = (
            db.session.query(Job)
            .filter_by(id=project_id, manager_id=manager)
            .options(joinedload(Job.batches).joinedload(Batch.tasks))
            .first()
        )

        if not project:
            return error_response("Project not found", 404)

        batch_ids = [b.id for b in project.batches]
        batch_members_rows = BatchMember.query.filter(BatchMember.batch_id.in_(batch_ids)).all()

        batch_members_map = {}
        for bm in batch_members_rows:
            members = []
            if bm.team_members:
                try:
                    members = json.loads(bm.team_members)
                except Exception:
                    names = [n.strip() for n in bm.team_members.split(",") if n.strip()]
                    members = [{"id": 0, "username": name} for name in names]
            batch_members_map.setdefault(bm.batch_id, []).extend(members)

        # Remove duplicates
        for batch_id, members in batch_members_map.items():
            unique = {m["id"] if m["id"] else m["username"]: m for m in members}
            batch_members_map[batch_id] = list(unique.values())

        project_data = {
            "project": {
                "job_id": project.id,
                "title": project.title,
                "description": project.description,
                "status": project.status,
                "skills_required": project.skills_required,
                "project_type": project.project_type,
                "created_at": project.created_at.isoformat() if project.created_at else None,
            },
            "batches": [],
        }

        for batch in project.batches:
            batch_data = batch.to_dict(include_tasks=True)
            batch_data["tasks"] = [t.to_dict(include_freelancer=True) for t in batch.tasks]
            batch_data["team_members"] = batch_members_map.get(batch.id, [])
            project_data["batches"].append(batch_data)

        return jsonify({"status": "success", "data": project_data}), 200

    except Exception as e:
        print("Get full project error:", repr(e))
        return error_response("Internal server error", 500)


# ---------- Tasks ----------
@bp.route("/tasks", methods=["POST"])
@secure_jwt_required
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
@secure_jwt_required
def create_task_route():
    try:
        data = request.get_json()
        if not data:
            return error_response("No JSON body provided", 400)

        manager_id_val = get_current_manager_id()
        data["assigned_by"] = manager_id_val

        task = create_task(data)
        return success_response("Task created successfully", task)

    except ValueError as ve:
        return error_response(str(ve), 400)
    except SQLAlchemyError as db_err:
        db.session.rollback()
        print("Database error:", repr(db_err))
        return error_response("Internal server error", 500)
    except Exception as e:
        print("Task creation error:", repr(e))
        return error_response("Internal server error", 500)


@bp.route("/tasks/status", methods=["PATCH"])
@secure_jwt_required
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
@secure_jwt_required
def list_batches():
    manager_id_val = get_current_manager_id()
    batches = get_batches_by_manager(manager_id_val)
    return jsonify({"status": "success", "data": batches}), 200


@bp.route("/batches", methods=["POST"])
@secure_jwt_required
def create_batch_route():
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
@secure_jwt_required
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
@secure_jwt_required
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
@secure_jwt_required
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
@secure_jwt_required
def batch_members():
    data = request.json
    batch_id = data.get("batch_id")
    if not batch_id:
        return error_response("batch_id is required", 400)
    members = get_batch_members(batch_id)
    return jsonify({"status": "success", "batch_id": batch_id, "members": members["team_members"]})


# ---------- Assign Freelancers ----------
@bp.route("/assign-freelancer-to-project", methods=["POST"])
@secure_jwt_required
def assign_freelancer_to_project():
    data = request.get_json()
    batch_id = data.get("batch_id")

    freelancer_ids = []
    if "freelancer_ids" in data and isinstance(data["freelancer_ids"], list):
        freelancer_ids = data["freelancer_ids"]
    elif "freelancer_id" in data:
        freelancer_ids = [data["freelancer_id"]]

    manager_id_val = get_current_manager_id()
    result = assign_freelancers_to_batch(manager_id_val, batch_id, freelancer_ids)
    return jsonify(result)


# ---------- Update Batch ----------
@bp.route("/batches/<int:batch_id>", methods=["PATCH"])
@secure_jwt_required
def update_batch_route(batch_id):
    if not require_manager():
        return error_response("Managers only", 403)
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)

        updated_batch = edit_batch(manager_id(), batch_id, data)
        return success_response("Batch updated successfully", updated_batch)
    except ValueError as ve:
        return error_response(str(ve), 400)
    except PermissionError as pe:
        return error_response(str(pe), 403)
    except Exception as e:
        print("Batch update error:", repr(e))
        return error_response("Internal server error", 500)


# ---------- Update Task ----------
@bp.route("/tasks/<int:task_id>", methods=["PATCH"])
@secure_jwt_required
def update_task_route(task_id):
    try:
        data = request.get_json()
        print("task data: ",data)
        updated = edit_task(manager_id(), task_id, data)
        print("Updated data : ",updated)
        return success_response("Task updated successfully", updated)
    except ValueError as ve:
        return error_response(str(ve), 404)
    except PermissionError as pe:
        return error_response(str(pe), 403)
    except Exception as e:
        print("Task update error:", repr(e))
        return error_response("Internal server error", 500)
