from app.models.application import Application
from app.repositories.application_repository import (
    save_application,
    get_applications_by_job,
    update_application_status,
    get_application_by_id
)
from datetime import datetime, timezone

def apply_to_job(freelancer_id, job_id, cover_letter):
    application = Application(
        freelancer_id=freelancer_id,
        job_id=job_id,
        cover_letter=cover_letter,
        applied_at=datetime.now(timezone.utc),  # timezone-aware UTC time
        status="Pending"
    )
    save_application(application)
    return application

def list_applicants(job_id):
    return get_applications_by_job(job_id)

def change_application_status(application_id, status):
    application = get_application_by_id(application_id)
    if not application:
        return None
    application.status = status
    application.updated_at = datetime.now(timezone.utc)  # timezone-aware UTC time
    update_application_status(application_id, status)
    return application