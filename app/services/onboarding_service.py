# app/services/onboarding_service.py

from app.repositories.onboarding_repository import (
    create_onboarding,
    get_onboarding_by_id,
    get_onboarding_by_freelancer_id,
    update_onboarding_status,
    get_all_onboardings
)
from app.repositories.user_repository import get_user_by_id
from app.models.onboarding_model import OnboardingStatus
from app import db


def create_onboarding_entry_service(data):
    freelancer_id = data.get("freelancer_id")
    job_id = data.get("job_id")

    if not freelancer_id or not job_id:
        raise Exception("freelancer_id and job_id are required")

    if not get_user_by_id(freelancer_id):
        raise Exception("Freelancer not found")

    existing = get_onboarding_by_freelancer_id(db.session, freelancer_id)
    if existing:
        raise Exception("Onboarding already exists for this freelancer")

    return create_onboarding(
        db.session,
        freelancer_id=freelancer_id,
        job_id=job_id,
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        notes=data.get("notes")
    )


def get_all_onboardings_service():
    return get_all_onboardings(db.session)


def assign_onboarding_to_user_service(data):
    # Same logic as create for now
    return create_onboarding_entry_service(data)


def update_onboarding_status_by_admin_service(data):
    onboarding_id = data.get("onboarding_id")
    new_status = data.get("status")

    if not onboarding_id or not new_status:
        raise Exception("onboarding_id and status are required")

    if new_status not in OnboardingStatus.__members__:
        raise Exception("Invalid status")

    return update_onboarding_status(
        db.session,
        onboarding_id=onboarding_id,
        new_status=OnboardingStatus[new_status]
    )


def get_freelancer_onboarding_steps(freelancer_id):
    return get_onboarding_by_freelancer_id(db.session, freelancer_id)


def update_onboarding_status_by_freelancer(data):
    freelancer_id = data.get("freelancer_id")
    onboarding_id = data.get("onboarding_id")
    new_status = data.get("status")

    if not freelancer_id or not onboarding_id or not new_status:
        raise Exception("freelancer_id, onboarding_id, and status are required")

    onboarding_list = get_onboarding_by_freelancer_id(db.session, freelancer_id)
    if not onboarding_list:
        raise Exception("No onboarding found for freelancer")

    if new_status not in OnboardingStatus.__members__:
        raise Exception("Invalid status")

    return update_onboarding_status(
        db.session,
        onboarding_id=onboarding_id,
        new_status=OnboardingStatus[new_status]
    )
