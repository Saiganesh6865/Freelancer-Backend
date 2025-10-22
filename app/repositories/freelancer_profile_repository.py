# app/repositories/freelancer_profile_repository.py
from app import db
from app.models.freelancer_profile import FreelancerProfile


def save_profile(profile):
    db.session.add(profile)
    db.session.commit()

def get_profile_by_user_id(user_id):
    return FreelancerProfile.query.filter_by(user_id=user_id).first()

def update_profile(user_id, data):
    profile = FreelancerProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return False, "Profile not found"

    profile.full_name = data.get("full_name", profile.full_name)
    profile.bio = data.get("bio", profile.bio)
    profile.skills = data.get("skills", profile.skills)
    profile.experience_years = data.get("experience_years", profile.experience_years)

    db.session.commit()
    return True, None
