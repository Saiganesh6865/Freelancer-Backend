from app import db
from datetime import datetime, timezone

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False)
    description = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default="pending")
    deadline = db.Column(db.DateTime, nullable=True)
    assign_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    assigned_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Relationships
    job = db.relationship("Job", back_populates="tasks")
    batch = db.relationship("Batch", back_populates="tasks")
    assigned_by_user = db.relationship("User", foreign_keys=[assigned_by], backref="tasks_assigned")
    assigned_to_user = db.relationship("User", foreign_keys=[assigned_to], backref="tasks_received")

    def to_dict(self, include_job=False, include_batch=False, include_freelancer=False):
        data = {
            "id": self.id,
            "title": self.title,
            "count": self.count,
            "description": self.description,
            "status": self.status,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "assign_date": self.assign_date.isoformat() if self.assign_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "assigned_by": self.assigned_by,
            "assigned_to": self.assigned_to,
        }

        if include_job and self.job:
            data["job"] = {
                "id": self.job.id,
                "title": self.job.title,
                "project_type": self.job.project_type,
            }

        if include_batch and self.batch:
            data["batch"] = {
                "id": self.batch.id,
                "project_name": self.batch.project_name,
                "project_type": self.batch.project_type,
            }

        if include_freelancer and self.assigned_to_user:
            data["freelancer"] = {
                "id": self.assigned_to_user.id,
                "username": self.assigned_to_user.username,
                "email": self.assigned_to_user.email,
            }

        return data
