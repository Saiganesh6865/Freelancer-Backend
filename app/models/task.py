# app/models/task.py
from app import db
from datetime import datetime

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)  # <-- fixed
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    count = db.Column(db.Integer, default=1)
    deadline = db.Column(db.DateTime, nullable=True)
    assign_date = db.Column(db.DateTime, default=datetime.utcnow)
    extra_metadata = db.Column(db.JSON, nullable=True)
    assigned_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship back to Job
    job = db.relationship("Job", back_populates="tasks")
