from app.models.application import Application
from app.repositories.application_repository import (
    save_application,
    get_applications_by_job,
    update_application_status,
    get_application_by_id
)
from datetime import datetime, timezone
from app.repositories import application_repository
from app.models.batch import Batch

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
    app = update_application_status(application_id, status)

    if app and status == "accepted":
        batch_id = app.batch_id
        freelancer_id = app.freelancer_id
        batch = Batch.query.get(batch_id)
        if batch:
            from app.repositories.batch_repository import add_freelancer_to_batch
            add_freelancer_to_batch(
                batch_id=batch.id,
                project_id=batch.job_id,
                manager_id=batch.created_by,
                freelancer_id=freelancer_id
            )

    return app.to_dict() if app else None


# Freelancer applies to a batch
def apply_to_batch(freelancer_id, batch_id):
    return application_repository.create_application(freelancer_id, batch_id)

# Freelancer views their applications
def get_freelancer_applications(freelancer_id):
    return application_repository.fetch_applications_by_freelancer(freelancer_id)

# Manager views all applications for a batch
def list_applications_for_batch(batch_id):
    return application_repository.get_applications_by_batch(batch_id)

# Manager reviews an application (accept/reject)
def review_application(application_id, decision):
    if decision not in ["accepted", "rejected"]:
        return None, "Invalid decision"
    application = application_repository.update_application_status(application_id, decision)
    if not application:
        return None, "Application not found"
    return application, None