# app\repositories\job_repository.py

from app import db
from app.models.job import Job

def create_job(title, description, project_type, created_by, skills_required=None, status="open"):
    job = Job(
        title=title,
        description=description,
        project_type=project_type,
        created_by=created_by,
        skills_required=skills_required,
        status=status
    )
    db.session.add(job)
    db.session.commit()
    return job


def save_job(job):
    db.session.add(job)
    db.session.commit()

def fetch_all_jobs():
    return Job.query.all()

def fetch_open_jobs():
    return Job.query.filter_by(status="open").all()

def count_total_jobs():
    return Job.query.count()

def count_completed_jobs():
    return Job.query.filter_by(status="completed").count()


# app/repositories/job_repository.py
def assign_manager_to_job(project_id, manager_id):
    job = Job.query.get(project_id)
    if not job:
        raise Exception("Project not found")

    job.manager_id = manager_id
    db.session.add(job)
    db.session.commit()
    return job
