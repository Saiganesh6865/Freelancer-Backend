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

# ---------- Profile ----------
def create_freelancer_profile(user_id, data):
    existing = get_profile_by_user_id(user_id)
    if existing:
        return False, "Profile already exists. Use update instead."
    profile = FreelancerProfile(
        user_id=user_id,
        full_name=data.get("full_name"),
        bio=data.get("bio"),
        skills=data.get("skills"),
        experience_years=data.get("experience_years")
    )
    save_profile(profile)
    return True, None

def get_freelancer_profile(user_id):
    profile = get_profile_by_user_id(user_id)
    if not profile:
        return None
    return {
        "id": profile.id,
        "full_name": profile.full_name,
        "bio": profile.bio,
        "skills": profile.skills.split(",") if profile.skills else [],
        "experience_years": profile.experience_years
    }

def update_freelancer_profile(user_id, data):
    return update_profile(user_id, data)

# ---------- Jobs ----------
def get_active_jobs():
    jobs = fetch_all_active_jobs()
    return [job.to_dict() for job in jobs]

# ---------- Suggested Batches ----------
def get_suggested_batches(freelancer_id):
    profile = FreelancerProfile.query.filter_by(user_id=freelancer_id).first()
    if not profile or not profile.skills:
        return []

    freelancer_skills = [s.strip().lower() for s in profile.skills.split(",")]
    batches = Batch.query.all()
    suggested = []

    # Get freelancer username
    freelancer = User.query.get(freelancer_id)
    freelancer_username = freelancer.username if freelancer else str(freelancer_id)

    for batch in batches:
        if not batch.skills_required:
            continue

        batch_skills = [s.strip().lower() for s in batch.skills_required.split(",")]
        if not any(skill in batch_skills for skill in freelancer_skills):
            continue

        # Check if freelancer is already in batch members using username
        member_in_batch = False
        batch_members = BatchMember.query.filter_by(batch_id=batch.id).all()
        for member in batch_members:
            if freelancer_username in member.get_team_members():  
                member_in_batch = True
                break

        batch_dict = batch.to_dict()
        batch_dict["already_applied"] = member_in_batch
        suggested.append(batch_dict)

    return suggested

# ---------- Applications ----------
def apply_for_batch(freelancer_id, batch_id):
    # First, check if already applied or member
    batch = Batch.query.get(batch_id)
    if not batch:
        return None, "Batch not found"

    for member in batch.members:
        if str(freelancer_id) in member.get_team_members():
            return None, "Already applied"

    existing = get_application(freelancer_id, batch_id)
    if existing:
        return None, "Already applied"

    application = create_application(freelancer_id, batch_id)
    return application.to_dict(), None

def list_my_applications(freelancer_id):
    apps = get_applications_by_freelancer(freelancer_id)
    return [a.to_dict() for a in apps]

# ---------- Tasks ----------
def get_my_tasks(freelancer_id):
    tasks = (
        db.session.query(Task)
        .join(Job, Job.id == Task.job_id)
        .join(Batch, Batch.id == Task.batch_id)
        .filter(Task.assigned_to == freelancer_id)
        .all()
    )
    return [t.to_dict(include_job=True, include_batch=True) for t in tasks]


#--------------------------My Batches---------------------------
def get_my_batches(freelancer_id):
    """
    Returns all batches where the freelancer is a member.
    """
    freelancer = User.query.get(freelancer_id)
    freelancer_name = freelancer.username.lower() if freelancer else str(freelancer_id).lower()

    # Fetch all batch memberships
    batch_memberships = BatchMember.query.all()
    my_batches = []
    print(f"Freelancer: {freelancer_name}")
    for membership in batch_memberships:
        print("Membership members:", membership.get_team_members())
        team_members = membership.get_team_members()  # This is a list of dicts or empty list
        # Extract names safely and lowercase them
        member_names = [m['name'].strip().lower() for m in team_members if 'name' in m and m['name']]

        if freelancer_name in member_names:
            batch = Batch.query.get(membership.batch_id)
            if batch:
                batch_dict = batch.to_dict()
                # Include batch member info
                batch_dict.update({
                    "manager_id": membership.manager_id,
                    "batch_member_id": membership.id,
                    "joined_at": membership.created_at.isoformat() if membership.created_at else None,
                    "team_members": [m.get('name') for m in team_members]  # Keep original names
                })
                my_batches.append(batch_dict)

    return my_batches
