from app import db
from datetime import datetime, timezone

class BatchMember(db.Model):
    __tablename__ = "batch_members"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False)
    project_id = db.Column(db.Integer, nullable=False)
    manager_id = db.Column(db.Integer, nullable=False)
    # Store usernames as a comma-separated string: "Alice,Bob,Charlie"
    team_members = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    batch = db.relationship("Batch", backref="members")

    def set_team_members(self, members):
        """
        Accepts a list of usernames and stores as a comma-separated string
        """
        if isinstance(members, list):
            self.team_members = ",".join(members)
        else:
            self.team_members = str(members)

    def get_team_members(self):
        """
        Returns a list of usernames from the stored comma-separated string
        """
        if not self.team_members:
            return []
        return [m.strip() for m in self.team_members.split(",") if m.strip()]

    def to_dict(self):
        return {
            "id": self.id,
            "batch_id": self.batch_id,
            "project_id": self.project_id,
            "manager_id": self.manager_id,
            "team_members": self.get_team_members(),  # returns list, not raw string
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
