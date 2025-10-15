# app/models/user.py
from app import db
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # admin, manager, freelancer
    # manager_type = db.Column(db.String(50), nullable=True)  # Only for managers
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    onboardings = relationship("Onboarding", back_populates="freelancer")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            # "manager_type": self.manager_type if self.role == 'manager' else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
