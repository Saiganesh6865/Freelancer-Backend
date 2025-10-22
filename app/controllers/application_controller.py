from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.application_service import (
    apply_to_job, list_applicants, change_application_status
)

bp = Blueprint('application_controller', __name__, url_prefix='/application')

@bp.route('/apply/<int:job_id>', methods=['POST'])
@jwt_required()
def apply(job_id):
    data = request.get_json()
    freelancer_id = int(get_jwt_identity())
    cover_letter = data.get("cover_letter")
     
    application = apply_to_job(freelancer_id, job_id, cover_letter)
    return jsonify({"message": "Application submitted", "application_id": application.id}), 200

@bp.route('/job/<int:job_id>/applicants', methods=['GET'])
@jwt_required()
def get_applicants(job_id):
    applicants = list_applicants(job_id)
    result = [
        {
            "id": app.id,
            "freelancer_id": app.freelancer_id,
            "cover_letter": app.cover_letter,
            "status": app.status,
            "applied_at": app.applied_at.isoformat()
        } for app in applicants
    ]
    return jsonify(result), 200

@bp.route('/<int:application_id>/status', methods=['PATCH'])
@jwt_required()
def update_status(application_id):
    data = request.get_json()
    new_status = data.get("status")
    updated_app = change_application_status(application_id, new_status)
    if not updated_app:
        return jsonify({"error": "Application not found"}), 404
    return jsonify({"message": "Status updated", "new_status": updated_app.status}), 200
