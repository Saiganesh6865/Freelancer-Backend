from app.repositories.freelancer_profile_repository import (
    save_profile,
    update_profile,
    get_profile_by_user_id
)
from app.repositories.job_repository import fetch_open_jobs as fetch_all_active_jobs
from app.repositories.application_repository import (
    create_application,
    fetch_applications_by_freelancer  # fixed import name
)
from app.models.freelancer_profile import FreelancerProfile

def create_freelancer_profile(user_id, data):
    try:
        existing = get_profile_by_user_id(user_id)
        if existing:
            return False, "Profile already exists. Use update instead."

        profile = FreelancerProfile(
            user_id=user_id,
            full_name=data.get("full_name"),
            bio=data.get("bio"),
            skills=data.get("skills"),
            experience_years=data.get("experience_years")
        )
        save_profile(profile)
        return True, None
    except Exception as e:
        return False, str(e)

def update_freelancer_profile(user_id, data):
    return update_profile(user_id, data)

def get_active_jobs():
    jobs = fetch_all_active_jobs()
    return [job.to_dict() for job in jobs]

def apply_to_job(user_id, job_id):
    return create_application(user_id, job_id)

def get_my_applications(user_id):
    applications = fetch_applications_by_freelancer(user_id)  # fixed usage here
    return [a.to_dict() for a in applications]
