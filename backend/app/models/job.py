# app/models/job.py
from app import db
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    description_file = db.Column(db.LargeBinary, nullable=True)

    skills_required = db.Column(db.Text, nullable=True)  # optional for annotation
    
    # budget = db.Column(db.Float, nullable=True)          # optional for annotation
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Admin who created it
    project_type = db.Column(db.String(50), nullable=False)  # 'annotation' or 'it'

    # work_type = db.Column(db.String(20), default='fixed')
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    onboardings = relationship("Onboarding", back_populates="job")
    tasks = relationship("Task", back_populates="job", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "skills_required": self.skills_required,
            "budget": self.budget,
            "client_id": self.client_id,
            "created_by": self.created_by,
            "project_type": self.project_type,
            "work_type": self.work_type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
