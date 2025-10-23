# app/controllers/job_controller.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.job_service import create_job, list_all_jobs
from app.services.job_service import (
    create_job,
    list_all_jobs,
    list_open_jobs  
)


bp = Blueprint('job_controller', __name__, url_prefix='/job')

# @bp.route('/post_job', methods=['POST'])
# @jwt_required()
# def post_job():
#     data = request.get_json()
#     user_id = get_jwt_identity()

#     job, error = create_job(data, user_id)
#     if error:
#         return jsonify({'error': error}), 400

#     return jsonify({'message': 'Job posted successfully', 'job_id': job.id}), 200

# @bp.route('/posted_jobs', methods=['GET'])
# @jwt_required()
# def get_all_jobs():
#     jobs = list_all_jobs()
#     return jsonify([{
#         'id': job.id,
#         'title': job.title,
#         'description': job.description,
#         'skills_required': job.skills_required,
#         'budget': job.budget,
#         'work_type': job.work_type,
#         'status': job.status,
#         'client_id': job.client_id
#     } for job in jobs])


# @bp.route('/available_jobs', methods=['GET'])
# @jwt_required()
# def available_jobs():
#     jobs = list_open_jobs()  # ✅ Only jobs with status 'open'
#     return jsonify([{
#         'id': job.id,
#         'title': job.title,
#         'description': job.description,
#         'skills_required': job.skills_required,
#         'budget': job.budget,
#         'work_type': job.work_type,
#         'status': job.status
#     } for job in jobs])
