from app import db
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref

class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    description_file = db.Column(db.LargeBinary, nullable=True)
    skills_required = db.Column(db.Text, nullable=True)
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    project_type = db.Column(db.String(50), nullable=False)  # 'annotation' or 'it'
    status = db.Column(db.String(20), default="open")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    deadline = db.Column(db.DateTime, nullable=True)

    # Relationships
    manager = relationship("User", foreign_keys=[manager_id], backref=backref("managed_jobs", lazy=True))
    created_by_user = relationship("User", foreign_keys=[created_by], backref=backref("created_jobs", lazy=True))
    onboardings = relationship("Onboarding", back_populates="job")
    tasks = relationship("Task", back_populates="job", cascade="all, delete-orphan")
    batches = relationship("Batch", back_populates="job", cascade="all, delete-orphan")

    # manager = relationship("User", foreign_keys=[manager_id], backref=backref("managed_jobs", lazy=True))
    # onboardings = relationship("Onboarding", back_populates="job")
    # tasks = relationship("Task", back_populates="job", cascade="all, delete-orphan")
    # batches = relationship("Batch", back_populates="job", cascade="all, delete-orphan")  # ✅ add this

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "skills_required": self.skills_required,
            "client_id": self.client_id,
            "created_by": self.created_by,
            "created_by_username": self.created_by_user.username if self.created_by_user else None,  # ✅ add this
            "project_type": self.project_type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "manager_id": self.manager_id,
            "manager_username": self.manager.username if self.manager else None,
        }

