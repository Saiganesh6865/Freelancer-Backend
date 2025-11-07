from app import db
from datetime import datetime, timezone
import json

class BatchMember(db.Model):
    __tablename__ = "batch_members"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False)
    project_id = db.Column(db.Integer, nullable=False)
    manager_id = db.Column(db.Integer, nullable=False)
    team_members = db.Column(db.Text, nullable=True)  # JSON list of dicts with assigned_count
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    batch = db.relationship("Batch", backref="members")

    def set_team_members(self, members):
        """
        members: list of dicts [{'id':1,'name':'abc','assigned_count':0}, ...]
        """
        self.team_members = json.dumps(members)

    def get_team_members(self):
        if not self.team_members:
            return []
        try:
            return json.loads(self.team_members)
        except Exception:
            return []

    def to_dict(self):
        return {
            "id": self.id,
            "batch_id": self.batch_id,
            "project_id": self.project_id,
            "manager_id": self.manager_id,
            "team_members": self.get_team_members(),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
