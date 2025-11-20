from app import db

class ManagerProfile(db.Model):
    __tablename__ = "manager_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)

    # Manager fields
    full_name = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    department = db.Column(db.String(255))
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    manager_type = db.Column(db.String(50))

    user = db.relationship("User", back_populates="manager_profile")

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "manager_type": self.manager_type,
            "full_name": self.full_name,
            "phone": self.phone,
            "department": self.department,
        }
