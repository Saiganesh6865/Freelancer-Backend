# app/controllers/manager_controller.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.repositories.user_repository import is_manager_request
from app.services.manager_service import (
    get_manager_dashboard_data,
    create_job_for_manager,
    get_jobs_by_manager
)
from app.utils.response import error_response

bp = Blueprint("manager", __name__, url_prefix="/manager")

@bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    if not is_manager_request():
        return error_response("Only managers allowed", 403)

    manager_id = get_jwt_identity()
    data = get_manager_dashboard_data(manager_id)
    return jsonify(data), 200


@bp.route("/jobs", methods=["POST"])
@jwt_required()
def create_job():
    if not is_manager_request():
        return error_response("Only managers allowed", 403)

    data = request.get_json()
    manager_id = get_jwt_identity()
    success, error = create_job_for_manager(manager_id, data)
    if not success:
        return error_response(error or "Job creation failed", 400)
    return jsonify({"message": "Job created successfully"}), 201


@bp.route("/jobs", methods=["GET"])
@jwt_required()
def list_jobs():
    if not is_manager_request():
        return error_response("Only managers allowed", 403)

    manager_id = get_jwt_identity()
    jobs = get_jobs_by_manager(manager_id)
    return jsonify(jobs), 200
