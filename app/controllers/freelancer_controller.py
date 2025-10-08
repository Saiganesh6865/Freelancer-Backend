from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.freelancer_service import (
    create_freelancer_profile,
    get_freelancer_profile,
    get_active_jobs,
    list_my_applications,
    update_freelancer_profile,
    get_my_tasks,
    apply_for_batch,
    get_suggested_batches,
    get_my_batches
)
from app.services.onboarding_service import (
    get_freelancer_onboarding_steps,
    update_onboarding_status_by_freelancer
)
from app.repositories.user_repository import is_freelancer_request
from app.utils.response import error_response, success_response
from app.services import task_service

bp = Blueprint('freelancer', __name__, url_prefix='/freelancer')


# ---------- Profile ----------
@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    user_id = get_jwt_identity()
    profile = get_freelancer_profile(user_id)
    if not profile:
        return error_response("Profile not found", 404)
    return success_response("Freelancer profile fetched", profile)


@bp.route('/create_profile', methods=['POST'])
@jwt_required()
def create_profile():
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    user_id = get_jwt_identity()
    data = request.get_json() or {}
    success, error = create_freelancer_profile(user_id, data)
    if error:
        return error_response(error, 400)
    return jsonify({"message": "Profile created successfully"}), 200


@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    user_id = get_jwt_identity()
    data = request.get_json() or {}
    success, error = update_freelancer_profile(user_id, data)
    if not success:
        return error_response(error, 400)
    return jsonify({"message": "Profile updated successfully"}), 200


# ---------- Jobs ----------
@bp.route('/jobs', methods=['GET'])
@jwt_required()
def list_jobs():
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    jobs = get_active_jobs()
    return jsonify(jobs), 200


# ---------- Applications ----------
@bp.route('/applications/batch', methods=['POST'])
@jwt_required()
def apply_batch():
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    user_id = get_jwt_identity()
    data = request.get_json() or {}
    batch_id = data.get("batch_id")

    if not batch_id:
        return error_response("batch_id is required", 400)

    app, err = apply_for_batch(user_id, batch_id)
    if err:
        return error_response(err, 400)

    return jsonify({"message": "Applied successfully", "application": app}), 200


@bp.route('/applications/mine', methods=['GET'])
@jwt_required()
def my_applications():
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    user_id = get_jwt_identity()
    apps = list_my_applications(user_id)
    return jsonify(apps), 200


# ---------- Onboarding ----------
@bp.route('/onboarding', methods=['GET'])
@jwt_required()
def view_onboarding():
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    freelancer_id = get_jwt_identity()
    steps = get_freelancer_onboarding_steps(freelancer_id)
    return success_response("Your onboarding steps", steps)


@bp.route('/onboarding/update-status', methods=['PATCH'])
@jwt_required()
def update_onboarding_status():
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    freelancer_id = get_jwt_identity()
    data = request.get_json() or {}
    data["freelancer_id"] = freelancer_id

    updated = update_onboarding_status_by_freelancer(data)
    return success_response("Step status updated", updated)


# ---------- Tasks ----------
# ---------- Tasks ----------
@bp.route('/tasks', methods=['GET'])
@jwt_required()
def my_tasks():
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    username = get_jwt_identity()  # assuming your JWT identity = username
    try:
        tasks = task_service.fetch_user_tasks(username)
        return success_response("Your assigned tasks", [t.to_dict() for t in tasks])
    except Exception as e:
        print("Freelancer tasks error:", repr(e))
        return error_response("Internal server error", 500)


@bp.route("/tasks/status", methods=["PATCH"])
@jwt_required()
def update_task_status_freelancer():
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    username = get_jwt_identity()
    data = request.get_json() or {}
    task_id = data.get("task_id")
    status = data.get("status")

    if not task_id or not status:
        return error_response("task_id and status are required", 400)

    try:
        task = task_service.change_task_status(task_id, status)
        if not task:
            return error_response("Task not found", 404)
        if task.assigned_to_username != username:
            return error_response("You can only update your own tasks", 403)
        return jsonify({"message": "Task status updated", "task": task.to_dict()}), 200
    except Exception as e:
        print("Freelancer task status update error:", repr(e))
        return error_response("Internal server error", 500)


# ---------- Suggested Batches ----------
@bp.route('/batches', methods=['GET'])
@jwt_required()
def list_available_batches():
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    user_id = get_jwt_identity()
    batches = get_suggested_batches(user_id)
    return jsonify(batches), 200


@bp.route('/batches/mine', methods=['GET'])
@jwt_required()
def my_batches():
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    freelancer_id = get_jwt_identity()
    batches = get_my_batches(freelancer_id)
    return success_response("Batches you are part of", batches)
