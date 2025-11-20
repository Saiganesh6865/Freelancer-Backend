from app import db
from datetime import datetime, timezone

class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    freelancer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False)
    status = db.Column(db.String(20), default="applied")
    applied_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))

    # Relationship to Batch
    batch = db.relationship("Batch", backref="applications")

    __table_args__ = (
        db.UniqueConstraint("freelancer_id", "batch_id", name="uq_freelancer_batch"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "freelancer_id": self.freelancer_id,
            "batch_id": self.batch_id,
            "status": self.status,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "project_name": self.batch.project_name if self.batch else None,
            "project_type": self.batch.project_type if self.batch else None,
        }
