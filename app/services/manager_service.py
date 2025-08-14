# app/services/manager_service.py
from app.repositories.manager_repository import (
    fetch_dashboard_metrics,
    insert_job,
    fetch_jobs_by_manager
)
from app.models.job import Job

def get_manager_dashboard_data(manager_id):
    return fetch_dashboard_metrics(manager_id)

def create_job_for_manager(manager_id, job_data):
    try:
        return insert_job(manager_id, job_data), None
    except Exception as e:
        return False, str(e)

def get_jobs_by_manager(manager_id):
    return [job.to_dict() for job in fetch_jobs_by_manager(manager_id)]


def fetch_jobs_by_manager(manager_id):
    return Job.query.filter_by(client_id=manager_id).all()
