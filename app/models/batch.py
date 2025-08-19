from app import db
from datetime import datetime

class Batch(db.Model):
    __tablename__ = "batches"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)  # Project relation
    project_name = db.Column(db.String(255), nullable=False)
    project_type = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, default=0)  # No. of tasks in this batch
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # Manager who created it
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks = db.relationship("Task", backref="batch", lazy=True)
