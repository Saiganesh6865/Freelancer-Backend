# app/models/task.py
from app import db
from datetime import datetime, timezone

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    count = db.Column(db.Integer, default=1)
    deadline = db.Column(db.DateTime, nullable=False)
    extra_metadata  = db.Column(db.JSON, nullable=True)  # extra details for annotation/IT
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    job = db.relationship("Job", back_populates="tasks")
