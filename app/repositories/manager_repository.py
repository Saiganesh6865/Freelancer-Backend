from app.models.job import Job
from app import db
from sqlalchemy import func
from app.models.manager_profile import ManagerProfile
from app.models.user import User

def get_manager_profile(user_id):
    return ManagerProfile.query.filter_by(user_id=user_id).first()


def create_empty_manager_profile(user: User):
    profile = ManagerProfile(
        user_id=user.id,
        username=user.username,
        email=user.email,
        manager_type=user.manager_type,
        full_name="",
        phone="",
        department=""
    )
    
    db.session.add(profile)
    db.session.commit()
    return profile


def update_manager_profile(user_id, data):
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")

    profile = get_manager_profile(user_id)
    if not profile:
        profile = create_empty_manager_profile(user)

    # Fields in manager_profiles
    profile_fields = [
        "full_name",
        "phone",
        "department",
        "username",
        "email",
        "manager_type"
    ]

    # Fields in users table
    user_fields = ["username", "email", "manager_type"]

    # Update manager_profiles fields
    for field in profile_fields:
        if field in data:
            setattr(profile, field, data[field])

    # Update users table fields
    for field in user_fields:
        if field in data:
            setattr(user, field, data[field])

    db.session.commit()
    return profile


def fetch_dashboard_metrics(manager_id):
    from app.models.application import Application

    total_jobs = db.session.query(func.count(Job.id)) \
        .filter_by(manager_id=manager_id).scalar()
    
    total_applications = db.session.query(func.count(Application.id)) \
        .join(Job, Job.id == Application.job_id) \
        .filter(Job.manager_id == manager_id).scalar()

    return {
        "total_jobs": total_jobs,
        "total_applications": total_applications,
    }

def insert_job(manager_id, job_data):
    if not job_data.get("title") or not job_data.get("description"):
        raise ValueError("Title and description are required")

    job = Job(
        title=job_data.get("title"),
        description=job_data.get("description"),
        skills_required=job_data.get("skills_required"),
        budget=job_data.get("budget"),
        work_type=job_data.get("work_type", "fixed"),
        status=job_data.get("status", "open"),
        manager_id=manager_id,
        created_by=manager_id
    )
    db.session.add(job)
    db.session.commit()
    return job

def fetch_jobs_by_manager(manager_id):
    jobs = Job.query.filter_by(manager_id=manager_id).order_by(Job.created_at.desc()).all()

    return [
        {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "skills_required": job.skills_required,
            "status": job.status,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "deadline": job.deadline.isoformat() if job.deadline else None,
            "project_id": job.id,   # ✅ use job.id consistently as project_id
            "manager_id": job.manager_id
        }
        for job in jobs
    ]
