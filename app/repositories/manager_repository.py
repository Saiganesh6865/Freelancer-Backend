from app.models.job import Job
from app import db
from sqlalchemy import func

def fetch_dashboard_metrics(manager_id):
    from app.models.application import Application

    total_jobs = db.session.query(func.count(Job.id))\
        .filter_by(manager_id=manager_id).scalar()
    
    total_applications = db.session.query(func.count(Application.id))\
        .join(Job, Job.id == Application.job_id)\
        .filter(Job.manager_id == manager_id).scalar()

    return {
        "total_jobs": total_jobs,
        "total_applications": total_applications,
    }

def insert_job(manager_id, job_data):
    job = Job(
        title=job_data.get("title"),
        description=job_data.get("description"),
        skills_required=job_data.get("skills_required"),
        budget=job_data.get("budget"),
        work_type=job_data.get("work_type", "fixed"),
        status=job_data.get("status", "open"),
        manager_id=manager_id,       # Fix: assign to manager_id, not client_id
        created_by=manager_id
    )
    db.session.add(job)
    db.session.commit()
    return job  # return the object so frontend can get ID

def fetch_jobs_by_manager(manager_id):
    return Job.query.filter_by(manager_id=manager_id).all()
