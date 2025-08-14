# app/models/application.py
from app import db
from datetime import datetime, timezone

class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    freelancer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(20), default="applied")  # applied, shortlisted, onboarded, rejected
    applied_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("freelancer_id", "job_id", name="uq_freelancer_job"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "freelancer_id": self.freelancer_id,
            "job_id": self.job_id,
            "cover_letter": self.cover_letter,
            "status": self.status,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None
        }
