# app/repositories/job_repository.py
from app import db
from app.models.job import Job

def create_job(title, description, project_type, created_by,  description_file=None, skills_required=None, budget=None, work_type="fixed", status="open", client_id=None):
    job = Job(
        title=title,
        description=description,
        description_file=description_file, 
        project_type=project_type,
        created_by=created_by,
        skills_required=skills_required,
        budget=budget,
        work_type=work_type,
        status=status,
        client_id=client_id
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
