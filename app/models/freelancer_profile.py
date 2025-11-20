# app/models/freelancer_profile.py
from app import db

class FreelancerProfile(db.Model):
    __tablename__ = "freelancer_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)

    # BASIC PROFILE
    full_name = db.Column(db.String(255))
    bio = db.Column(db.Text)
    skills = db.Column(db.Text)                   # CSV stored
    experience_years = db.Column(db.Integer)

    # NEW FIELDS (SUPPORT FRONTEND)
    portfolio_links = db.Column(db.Text)
    contact = db.Column(db.String(255))

    # COMPANY INFORMATION
    company_name = db.Column(db.String(255))
    designation = db.Column(db.String(255))
    department = db.Column(db.String(255))
    employment_type = db.Column(db.String(255))
    work_mode = db.Column(db.String(255))
    location = db.Column(db.String(255))
    joining_date = db.Column(db.String(255))
    manager_name = db.Column(db.String(255))
