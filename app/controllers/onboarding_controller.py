from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.services.onboarding_service import (
    create_onboarding_entry_service,
    get_all_onboardings_service,
    assign_onboarding_to_user_service,
    update_onboarding_status_by_admin_service
)
from app.utils.response import success_response, error_response
from app.repositories.user_repository import is_admin_request

bp = Blueprint("onboarding", __name__, url_prefix="/admin/onboarding")

@bp.route("", methods=["POST"])
@jwt_required()
def create_onboarding():
    if not is_admin_request():
        return error_response("Admins only", 403)

    data = request.get_json()
    step = create_onboarding_entry_service(data)
    return success_response("Onboarding step created", step)

@bp.route("", methods=["GET"])
@jwt_required()
def get_all_steps():
    if not is_admin_request():
        return error_response("Admins only", 403)

    steps = get_all_onboardings_service()
    return success_response("All onboarding steps", steps)

@bp.route("/assign", methods=["POST"])
@jwt_required()
def assign_step():
    if not is_admin_request():
        return error_response("Admins only", 403)

    data = request.get_json()
    assigned = assign_onboarding_to_user_service(data)
    return success_response("Step assigned to freelancer", assigned)

@bp.route("/update-status", methods=["PATCH"])
@jwt_required()
def update_step_status_by_admin():
    if not is_admin_request():
        return error_response("Admins only", 403)

    data = request.get_json()
    updated = update_onboarding_status_by_admin_service(data)
    return success_response("Onboarding step updated by admin", updated)
