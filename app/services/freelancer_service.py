from app.models.task import Task
from app.models.job import Job
from app.models.batch import Batch
from app.models.BatchMember import BatchMember
from app import db
from app.models.user import User

from app.repositories.freelancer_profile_repository import save_profile, update_profile, get_profile_by_user_id
from app.repositories.job_repository import fetch_open_jobs as fetch_all_active_jobs
from app.repositories.application_repository import (
    create_application, get_applications_by_freelancer, get_application
)
from app.models.freelancer_profile import FreelancerProfile

# ============================================================
#                     PROFILE FUNCTIONS
# ============================================================

def clean_skills_input(skills):
    """Ensure skills come as a clean list."""
    if not skills:
        return []

    if isinstance(skills, list):
        return [s.strip() for s in skills if s.strip()]

    if isinstance(skills, str):
        cleaned = (
            skills.replace("{", "")
                  .replace("}", "")
                  .replace('"', "")
                  .split(",")
        )
        return [s.strip() for s in cleaned if s.strip()]

    return []


def create_freelancer_profile(user_id, data):
    existing = get_profile_by_user_id(user_id)
    if existing:
        return False, "Profile already exists. Use update instead."

    skills = clean_skills_input(data.get("skills"))

    profile = FreelancerProfile(
        user_id=user_id,
        full_name=data.get("full_name"),
        bio=data.get("bio"),
        skills=",".join(skills),
        experience_years=data.get("experience_years"),

        # NEW FIELDS
        portfolio_links=data.get("portfolio_links"),
        contact=data.get("contact"),

        company_name=data.get("company_name"),
        designation=data.get("designation"),
        department=data.get("department"),
        employment_type=data.get("employment_type"),
        work_mode=data.get("work_mode"),
        location=data.get("location"),
        joining_date=data.get("joining_date"),
        manager_name=data.get("manager_name"),
    )

    save_profile(profile)
    return True, None




def get_freelancer_profile(user_id):
    profile = get_profile_by_user_id(user_id)
    if not profile:
        return None

    skills = clean_skills_input(profile.skills)

    return {
        "id": profile.id,
        "full_name": profile.full_name,
        "bio": profile.bio,
        "skills": skills,
        "experience_years": profile.experience_years,

        # NEW FIELDS
        "portfolio_links": profile.portfolio_links,
        "contact": profile.contact,

        "company_name": profile.company_name,
        "designation": profile.designation,
        "department": profile.department,
        "employment_type": profile.employment_type,
        "work_mode": profile.work_mode,
        "location": profile.location,
        "joining_date": profile.joining_date,
        "manager_name": profile.manager_name,
    }


def update_freelancer_profile(user_id, data):
    # Clean skills if needed
    if "skills" in data:
        skills = clean_skills_input(data["skills"])
        data["skills"] = ",".join(skills)

    # Allow updating ALL fields
    allowed_fields = [
        "full_name", "bio", "skills", "experience_years",
        "portfolio_links", "contact",
        "company_name", "designation", "department",
        "employment_type", "work_mode", "location",
        "joining_date", "manager_name"
    ]

    clean_data = {field: data.get(field) for field in allowed_fields if field in data}

    return update_profile(user_id, clean_data)



# ============================================================
#                        JOBS
# ============================================================

def get_active_jobs():
    jobs = fetch_all_active_jobs()
    return [job.to_dict() for job in jobs]



# ============================================================
#                SUGGESTED BATCHES
# ============================================================

def get_suggested_batches(freelancer_id):
    profile = FreelancerProfile.query.filter_by(user_id=freelancer_id).first()
    if not profile or not profile.skills:
        return []

    freelancer_skills = clean_skills_input(profile.skills)
    freelancer_skills = [s.lower() for s in freelancer_skills]

    batches = Batch.query.all()
    suggested = []

    freelancer = User.query.get(freelancer_id)
    freelancer_username = freelancer.username if freelancer else str(freelancer_id)

    for batch in batches:
        if not batch.skills_required:
            continue

        batch_skills = [s.strip().lower() for s in batch.skills_required.split(",")]

        if not any(skill in batch_skills for skill in freelancer_skills):
            continue

        member_in_batch = any(
            freelancer_username in member.get_team_members()
            for member in batch.members
        )

        already_applied = member_in_batch or bool(get_application(freelancer_id, batch.id))

        batch_dict = batch.to_dict()
        batch_dict["already_applied"] = already_applied
        suggested.append(batch_dict)

    return suggested



# ============================================================
#                    APPLICATIONS
# ============================================================

def apply_for_batch(freelancer_id, batch_id):
    batch = Batch.query.get(batch_id)
    if not batch:
        return None, "Batch not found"

    # Already a member
    if any(str(freelancer_id) in member.get_team_members() for member in batch.members):
        return None, "Already applied"

    # Already applied
    if get_application(freelancer_id, batch_id):
        return None, "Already applied"

    application = create_application(freelancer_id, batch_id)
    return application.to_dict(), None



def list_my_applications(freelancer_id):
    apps = get_applications_by_freelancer(freelancer_id)
    return [a.to_dict() for a in apps]



# ============================================================
#                        TASKS
# ============================================================

def get_my_tasks(freelancer_id):
    tasks = (
        db.session.query(Task)
        .join(Job, Job.id == Task.job_id)
        .join(Batch, Batch.id == Task.batch_id)
        .filter(Task.assigned_to == freelancer_id)
        .all()
    )
    return [t.to_dict(include_job=True, include_batch=True) for t in tasks]



# ============================================================
#                   MY BATCHES
# ============================================================

def get_my_batches(freelancer_id):
    """Returns all batches where the freelancer is a member."""
    freelancer = User.query.get(freelancer_id)
    freelancer_name = freelancer.username.lower() if freelancer else str(freelancer_id).lower()

    batch_memberships = BatchMember.query.all()
    my_batches = []

    for membership in batch_memberships:
        team_members = membership.get_team_members()

        member_names = [
            m["name"].strip().lower()
            for m in team_members if "name" in m and m["name"]
        ]

        if freelancer_name in member_names:
            batch = Batch.query.get(membership.batch_id)
            if batch:
                batch_dict = batch.to_dict()
                batch_dict.update({
                    "manager_id": membership.manager_id,
                    "batch_member_id": membership.id,
                    "joined_at": membership.created_at.isoformat() if membership.created_at else None,
                    "team_members": [m.get("name") for m in team_members]
                })
                my_batches.append(batch_dict)

    return my_batches
