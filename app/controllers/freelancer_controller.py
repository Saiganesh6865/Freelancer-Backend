# app/controllers/freelancer_controller.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.freelancer_service import (
    create_freelancer_profile,
    get_active_jobs,
    apply_to_job,
    get_my_applications,
    update_freelancer_profile
)
from app.services.onboarding_service import (
    get_freelancer_onboarding_steps,
    update_onboarding_status_by_freelancer
)
from app.repositories.user_repository import is_freelancer_request
from app.utils.response import error_response, success_response

bp = Blueprint('freelancer', __name__, url_prefix='/freelancer')


@bp.route('/profile', methods=['POST'])
@jwt_required()
def create_profile():
    user_id = get_jwt_identity()
    data = request.get_json()

    success, error = create_freelancer_profile(user_id, data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "Profile created successfully"}), 200


@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    user_id = get_jwt_identity()
    data = request.get_json()

    success, error = update_freelancer_profile(user_id, data)
    if not success:
        return error_response(error, 400)

    return jsonify({"message": "Profile updated successfully"}), 200


@bp.route('/jobs', methods=['GET'])
@jwt_required()
def list_jobs():
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    jobs = get_active_jobs()
    return jsonify(jobs), 200


@bp.route('/applications', methods=['POST'])
@jwt_required()
def apply():
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    user_id = get_jwt_identity()
    data = request.get_json()
    job_id = data.get("job_id")

    success, error = apply_to_job(user_id, job_id)
    if not success:
        return error_response(error or "Application failed", 400)

    return jsonify({"message": "Applied successfully"}), 201


@bp.route('/applications/mine', methods=['GET'])
@jwt_required()
def my_applications():
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    user_id = get_jwt_identity()
    applications = get_my_applications(user_id)
    return jsonify(applications), 200


# 🆕 Onboarding Routes Below

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
    data = request.get_json()
    data["freelancer_id"] = freelancer_id

    updated = update_onboarding_status_by_freelancer(data)
    return success_response("Step status updated", updated)
