# app/models/project.py
from app import db
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

# app/models/project.py
class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    project_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    manager = relationship("User", backref="projects")

    # ✅ Match the Job side
    # jobs = relationship("Job", back_populates="project", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "project_type": self.project_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "manager_id": self.manager_id,
            "manager_name": self.manager.username if self.manager else None,
            "jobs": [job.to_dict() for job in self.jobs] if self.jobs else [],
        }
