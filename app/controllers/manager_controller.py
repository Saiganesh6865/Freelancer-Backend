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
from sqlalchemy.orm import joinedload

from app import db
from app.models.user import User
from app.models.BatchMember import BatchMember
from app.models.job import Job
from app.models.batch import Batch
from app.models.task import Task

import json
from app.services.task_service import edit_task


bp = Blueprint("manager", __name__, url_prefix="/manager")


# -----------------------------------------------------
#                  SECURITY WRAPPER
# -----------------------------------------------------
def secure_jwt_required(fn):
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return jwt_required()(wrapper)


def require_manager():
    return is_manager_request()


def manager_id():
    identity = get_jwt_identity()
    try:
        return int(identity)
    except Exception:
        return identity


# -----------------------------------------------------
#                 DASHBOARD
# -----------------------------------------------------
@bp.route("/dashboard", methods=["GET"])
@secure_jwt_required
def dashboard():
    if not require_manager():
        return error_response("Managers only", 403)
    try:
        data = get_manager_dashboard_data(manager_id())
        return success_response("Dashboard fetched", data)
    except Exception as e:
        print("Dashboard error:", e)
        return error_response("Internal error", 500)


# -----------------------------------------------------
#           MANAGER PROFILE (GET + UPDATE)
# -----------------------------------------------------
@bp.route("/profile", methods=["GET"])
@secure_jwt_required
def get_manager_profile_route():
    if not require_manager():
        return error_response("Managers only", 403)

    from app.repositories.manager_repository import (
        get_manager_profile,
        create_empty_manager_profile
    )

    user_id = manager_id()
    profile = get_manager_profile(user_id)

    if not profile:
        profile = create_empty_manager_profile(User.query.get(user_id))

    return success_response("Profile fetched", profile.to_dict())



@bp.route("/profile", methods=["PUT"])
@secure_jwt_required
def update_manager_profile_route():
    if not require_manager():
        return error_response("Managers only", 403)

    data = request.get_json() or {}
    user_id = manager_id()

    from app.repositories.manager_repository import update_manager_profile
    updated = update_manager_profile(user_id, data)

    return success_response("Profile updated successfully", updated.to_dict())



# -----------------------------------------------------
#                     PROJECTS
# -----------------------------------------------------
@bp.route("/projects", methods=["GET"])
@secure_jwt_required
def projects():
    if not require_manager():
        return error_response("Managers only", 403)
    try:
        data = get_manager_jobs(manager_id())
        return success_response("Projects fetched", data)
    except Exception as e:
        print("Projects error:", e)
        return error_response("Internal server error", 500)


# -----------------------------------------------------
#               SINGLE PROJECT WITH BATCHES
# -----------------------------------------------------
@bp.route("/projects/<int:project_id>", methods=["GET"])
@secure_jwt_required
def get_full_project(project_id):
    if not require_manager():
        return error_response("Managers only", 403)

    try:
        mid = manager_id()

        project = (
            db.session.query(Job)
            .filter_by(id=project_id, manager_id=mid)
            .options(joinedload(Job.batches).joinedload(Batch.tasks))
            .first()
        )

        if not project:
            return error_response("Project not found", 404)

        batch_ids = [b.id for b in project.batches]
        batch_member_rows = BatchMember.query.filter(
            BatchMember.batch_id.in_(batch_ids)
        ).all()

        batch_members_map = {}

        for bm in batch_member_rows:
            members = []
            if bm.team_members:
                try:
                    members = json.loads(bm.team_members)
                except:
                    names = [x.strip() for x in bm.team_members.split(",")]
                    members = [{"id": 0, "username": n} for n in names]
            batch_members_map[bm.batch_id] = members

        result = {
            "project": {
                "job_id": project.id,
                "title": project.title,
                "description": project.description,
                "status": project.status,
                "skills_required": project.skills_required,
                "project_type": project.project_type,
                "created_at": project.created_at.isoformat(),
            },
            "batches": [],
        }

        for batch in project.batches:
            bdata = batch.to_dict(include_tasks=True)
            bdata["team_members"] = batch_members_map.get(batch.id, [])
            bdata["tasks"] = [t.to_dict(include_freelancer=True) for t in batch.tasks]
            result["batches"].append(bdata)

        return success_response("Project loaded", result)

    except Exception as e:
        print("Project fetch error:", e)
        return error_response("Internal server error", 500)


# -----------------------------------------------------
#                     TASK LIST
# -----------------------------------------------------
@bp.route("/tasks", methods=["POST"])
@secure_jwt_required
def get_tasks_route():
    if not require_manager():
        return error_response("Managers only", 403)

    data = request.get_json() or {}
    job_id = data.get("job_id")

    if not job_id:
        return error_response("job_id is required", 400)

    try:
        tasks = get_manager_tasks(manager_id(), job_id)
        return success_response("Tasks fetched", tasks)
    except Exception as e:
        print("Tasks error:", e)
        return error_response("Internal server error", 500)


# -----------------------------------------------------
#                    CREATE TASK
# -----------------------------------------------------
@bp.route("/assign_tasks", methods=["POST"])
@secure_jwt_required
def create_task_route():
    try:
        data = request.json or {}
        data["assigned_by"] = get_current_manager_id()
        task = create_task(data)
        return success_response("Task created", task)
    except Exception as e:
        db.session.rollback()
        print("Create task error:", e)
        return error_response("Internal server error", 500)


# -----------------------------------------------------
#                UPDATE TASK STATUS
# -----------------------------------------------------
@bp.route("/tasks/status", methods=["PATCH"])
@secure_jwt_required
def update_task_status_manager_route():
    if not require_manager():
        return error_response("Managers only", 403)

    data = request.json or {}
    task_id = data.get("task_id")
    status = data.get("status")

    if not task_id or not status:
        return error_response("task_id and status required", 400)

    try:
        task = change_task_status(manager_id(), task_id, status)
        return success_response("Task status updated", task)
    except Exception as e:
        print("Task status error:", e)
        return error_response("Internal server error", 500)


# -----------------------------------------------------
#                    BATCHES
# -----------------------------------------------------
@bp.route("/batches", methods=["GET"])
@secure_jwt_required
def list_batches():
    manager = get_current_manager_id()
    batches = get_batches_by_manager(manager)
    return success_response("Batches fetched", batches)


@bp.route("/batches", methods=["POST"])
@secure_jwt_required
def create_batch_route():
    if not require_manager():
        return error_response("Managers only", 403)
    data = request.json or {}

    try:
        batch = add_batch(manager_id(), data)
        return success_response("Batch created", batch)
    except Exception as e:
        print("Batch create error:", e)
        return error_response("Internal server error", 500)


# -----------------------------------------------------
#              FREELANCER LIST
# -----------------------------------------------------
@bp.route("/freelancers", methods=["GET"])
@secure_jwt_required
def freelancers():
    if not require_manager():
        return error_response("Managers only", 403)

    try:
        data = get_manager_freelancers(manager_id())
        return success_response("Freelancers fetched", data)
    except Exception as e:
        print("Freelancers error:", e)
        return error_response("Internal server error", 500)


# -----------------------------------------------------
#               APPLICATIONS
# -----------------------------------------------------
@bp.route("/batches/applications", methods=["POST"])
@secure_jwt_required
def list_batch_applications():
    if not require_manager():
        return error_response("Managers only", 403)

    data = request.json or {}
    batch_id = data.get("batch_id")

    if not batch_id:
        return error_response("batch_id is required", 400)

    try:
        applications = get_batch_applications(manager_id(), batch_id)
        return success_response("Applications fetched", applications)
    except Exception as e:
        print("Applications error:", e)
        return error_response("Internal server error", 500)


@bp.route("/batch_applications/status", methods=["PATCH"])
@secure_jwt_required
def update_application_status_route():
    if not require_manager():
        return error_response("Managers only", 403)

    data = request.json or {}
    application_id = data.get("application_id")
    status = data.get("status")

    if not application_id or status not in ["accepted", "rejected"]:
        return error_response("Invalid input", 400)

    try:
        updated = change_application_status(application_id, status)
        return success_response("Application updated", updated)
    except Exception as e:
        print("App status error:", e)
        return error_response("Internal server error", 500)


# -----------------------------------------------------
#           BATCH MEMBERS + ASSIGNMENT
# -----------------------------------------------------
@bp.route("/batch_members_list", methods=["POST"])
@secure_jwt_required
def batch_members():
    data = request.json
    batch_id = data.get("batch_id")

    if not batch_id:
        return error_response("batch_id is required", 400)

    members = get_batch_members(batch_id)
    return success_response("Members fetched", members["team_members"])


@bp.route("/assign-freelancer-to-project", methods=["POST"])
@secure_jwt_required
def assign_freelancer_to_project():
    data = request.json
    batch_id = data.get("batch_id")

    freelancer_ids = (
        data.get("freelancer_ids")
        if isinstance(data.get("freelancer_ids"), list)
        else [data.get("freelancer_id")]
    )

    result = assign_freelancers_to_batch(
        get_current_manager_id(),
        batch_id,
        freelancer_ids,
    )

    return jsonify(result)


# -----------------------------------------------------
#                    UPDATE BATCH
# -----------------------------------------------------
@bp.route("/batches/<int:batch_id>", methods=["PATCH"])
@secure_jwt_required
def update_batch_route(batch_id):
    if not require_manager():
        return error_response("Managers only", 403)

    try:
        data = request.json
        updated = edit_batch(manager_id(), batch_id, data)
        return success_response("Batch updated", updated)
    except Exception as e:
        print("Batch update error:", e)
        return error_response("Internal server error", 500)


# -----------------------------------------------------
#                     UPDATE TASK
# -----------------------------------------------------
@bp.route("/tasks/<int:task_id>", methods=["PATCH"])
@secure_jwt_required
def update_task_route(task_id):
    try:
        data = request.json
        updated = edit_task(manager_id(), task_id, data)
        return success_response("Task updated", updated)
    except Exception as e:
        print("Task update error:", e)
        return error_response("Internal server error", 500)
