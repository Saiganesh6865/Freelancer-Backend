# app/services/job_service.py
from app.repositories.job_repository import save_job, fetch_all_jobs
from app.models.job import Job
from app.repositories.job_repository import (
    save_job,
    fetch_all_jobs,
    fetch_open_jobs  # ✅ ADD this
)


def create_job(data, user_id):
    try:
        job = Job(
            title=data.get('title'),
            description=data.get('description'),
            skills_required=data.get('skills_required'),
            budget=data.get('budget'),
            client_id=user_id,
            work_type=data.get('work_type', 'fixed'),
            status=data.get('status', 'open')
        )
        save_job(job)
        return job, None
    except Exception as e:
        return None, str(e)

def list_all_jobs():
    return fetch_all_jobs()

def list_open_jobs():
    return fetch_open_jobs()