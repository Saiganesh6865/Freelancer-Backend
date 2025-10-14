from app import db
from datetime import datetime, timezone

class Batch(db.Model):
    __tablename__ = "batches"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)  # ✅ renamed for clarity
    project_name = db.Column(db.String(255), nullable=False)
    project_type = db.Column(db.String(50), nullable=False)
    count = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, nullable=False)   # same as manager_id
    skills_required = db.Column(db.Text, nullable=True)  # copied from Job
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # ✅ Relationships
    job = db.relationship("Job", back_populates="batches")
    tasks = db.relationship("Task", back_populates="batch", cascade="all, delete-orphan")

    def to_dict(self, include_tasks=False):
        data = {
            "id": self.id,
            "job_id": self.job_id,
            "project_name": self.project_name,
            "project_type": self.project_type,
            "count": self.count,
            "created_by": self.created_by,
            "skills_required": self.skills_required,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

        if include_tasks:
            data["tasks"] = [task.to_dict() for task in self.tasks]

        return data
