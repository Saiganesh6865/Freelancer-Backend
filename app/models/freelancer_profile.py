# app/models/freelancer_profile.py
from app import db

class FreelancerProfile(db.Model):
    __tablename__ = "freelancer_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)
    full_name = db.Column(db.String(255))
    bio = db.Column(db.Text)
    skills = db.Column(db.Text)
    experience_years = db.Column(db.Integer)