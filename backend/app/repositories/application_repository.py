from app import db
from app.models.application import Application
from datetime import datetime, timezone

def save_application(application):
    db.session.add(application)
    db.session.commit()

def get_applications_by_job(job_id):
    return Application.query.filter_by(job_id=job_id).all()

def fetch_applications_by_freelancer(freelancer_id):
    return Application.query.filter_by(freelancer_id=freelancer_id).all()

def get_application_by_id(application_id):
    return Application.query.get(application_id)

def update_application_status(application_id, status):
    app = get_application_by_id(application_id)
    if app:
        app.status = status
        app.updated_at = datetime.now(timezone.utc)
        db.session.commit()
    return app

def create_application(freelancer_id, job_id):
    new_app = Application(freelancer_id=freelancer_id, job_id=job_id)
    db.session.add(new_app)
    db.session.commit()
    return new_app
