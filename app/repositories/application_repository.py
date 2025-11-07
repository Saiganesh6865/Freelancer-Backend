from app import db
from app.models.application import Application

# Save
def save_application(application):
    db.session.add(application)
    db.session.commit()

# Get by batch
def get_applications_by_batch(batch_id):
    return Application.query.filter_by(batch_id=batch_id).all()

# Get by freelancer
def get_applications_by_freelancer(freelancer_id):
    return Application.query.filter_by(freelancer_id=freelancer_id).all()

# Get by ID
def get_application_by_id(application_id):
    return Application.query.get(application_id)

# 🔥 Helper: check if already applied
def get_application(freelancer_id, batch_id):
    return Application.query.filter_by(freelancer_id=freelancer_id, batch_id=batch_id).first()

def has_applied(freelancer_id, batch_id) -> bool:
    """Return True if freelancer already applied for this batch"""
    return Application.query.filter_by(freelancer_id=freelancer_id, batch_id=batch_id).first() is not None

# Update status
def update_application_status(application_id, status):
    app = get_application_by_id(application_id)
    if app:
        app.status = status
        db.session.commit()
    return app

# Create new application
def create_application(freelancer_id, batch_id):
    new_app = Application(freelancer_id=freelancer_id, batch_id=batch_id)
    db.session.add(new_app)
    db.session.commit()
    return new_app
