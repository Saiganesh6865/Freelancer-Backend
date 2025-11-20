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

    # Update ALL allowed fields
    for field, value in data.items():
        if hasattr(profile, field) and value is not None:
            setattr(profile, field, value)

    db.session.commit()
    return True, None
