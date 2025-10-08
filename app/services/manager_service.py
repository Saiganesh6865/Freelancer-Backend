from datetime import datetime
from dateutil import parser
from app.repositories.batch_repository import create_batch, get_batch_by_id
from app.repositories.task_repository import create_task
from app.repositories.manager_repository import fetch_dashboard_metrics
from app.repositories.application_repository import update_application_status
from app.models.batch import Batch
from app.models.job import Job
from app.models.BatchMember import BatchMember
from app.models.user import User
from app.models.application import Application
from app import db
import json

# ---------- Dashboard ----------
def get_manager_dashboard_data(manager_id):
    return fetch_dashboard_metrics(manager_id)

# ---------- Jobs ----------
def get_manager_jobs(manager_id):
    jobs = Job.query.filter_by(manager_id=manager_id).all()
    return [
        {
            "job_id": job.id,
            "title": job.title,
            "description": job.description,
            "status": job.status,
            "skills_required": job.skills_required,
            "created_at": job.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for job in jobs
    ]

# ---------- Tasks ----------
def get_manager_tasks(manager_id, job_id=None):
    from app.models.task import Task
    from app import db

    query = db.session.query(Task).join(Job, Job.id == Task.job_id).filter(Job.manager_id == manager_id)
    if job_id:
        query = query.filter(Task.job_id == job_id)

    tasks = query.all()
    return [t.to_dict(include_job=True, include_batch=True, include_freelancer=True) for t in tasks]

def add_task(manager_id, data):
    batch = get_batch_by_id(data["batch_id"])
    if not batch:
        raise ValueError("Invalid batch_id")
    if not data.get("job_id"):
        raise ValueError("job_id is required")

    deadline = parser.parse(data["deadline"]) if data.get("deadline") else None
    assign_date = parser.parse(data["assign_date"]) if data.get("assign_date") else datetime.utcnow()

    return create_task(
        job_id=data["job_id"],
        batch_id=batch.id,
        title=data["title"],
        count=data.get("count", 1),
        deadline=deadline,
        assign_date=assign_date,
        extra_metadata=data.get("metadata"),
        assigned_by=manager_id,
        assigned_to=data.get("assigned_to")
    ).to_dict()

def create_task_for_job(manager_id, data):
    return add_task(manager_id, data)


def change_task_status(manager_id, task_id, status):
    from app.models.task import Task

    task = (
        db.session.query(Task)
        .join(Job, Job.id == Task.job_id)
        .filter(Task.id == task_id, Job.manager_id == manager_id)
        .first()
    )
    if not task:
        raise ValueError("Task not found or unauthorized")

    task.status = status
    db.session.commit()
    return task.to_dict()

# ---------- Batches ----------
def get_manager_batches(manager_id):
    from app.repositories.batch_repository import get_batch_members
    batches = Batch.query.filter_by(created_by=manager_id).all()
    result = []
    for batch in batches:
        data = batch.to_dict()
        data["members"] = get_batch_members(batch.id)["team_members"]
        result.append(data)
    return result


def get_all_batches():
    return [batch.to_dict() for batch in Batch.query.all()]

def add_batch(manager_id, data):
    job_id = data.get("job_id") or data.get("project_id")
    print("Received job_id/project_id:", job_id)
    print("Logged-in manager_id:", manager_id)

    job = Job.query.get(job_id)
    print("Fetched job:", job)
    if job:
        print("Job manager_id:", job.manager_id)

    if not job or int(job.manager_id) != int(manager_id):
        raise ValueError("Invalid job_id or unauthorized manager")


    return create_batch(
    job_id=job.id,
    project_name=job.title,
    project_type=job.project_type if hasattr(job, "project_type") else data.get("project_type"),
    count=data.get("count", 0),
    created_by=manager_id,
    skills_required=job.skills_required
).to_dict()



# ---------- Freelancers ----------
def get_manager_freelancers(manager_id):
    from app.models.user import User
    from app.models.task import Task
    from app import db

    results = (
        db.session.query(User)
        .join(Task, Task.assigned_to == User.id)
        .join(Job, Job.id == Task.job_id)
        .filter(Job.manager_id == manager_id, User.role == "freelancer")
        .all()
    )
    return [u.to_dict() for u in results]

# ---------- Applications ----------
def get_batch_applications(manager_id, batch_id):
    batch = Batch.query.filter_by(id=batch_id).first()
    if not batch:
        return {"success": False, "error": "Batch not found"}

    if int(batch.created_by) != int(manager_id):
        return {"success": False, "error": "Batch not found or not owned by this manager"}

    applications = Application.query.filter_by(batch_id=batch_id).all()

    return {
        "success": True,
        "batch": batch.to_dict(),
        "applications": [app.to_dict() for app in applications]
    }


def change_application_status(application_id, status):
    app_obj = update_application_status(application_id, status)

    if app_obj and status == "accepted":
        batch_id = app_obj.batch_id
        freelancer_id = app_obj.freelancer_id

        batch = Batch.query.get(batch_id)
        freelancer = User.query.get(freelancer_id)

        if batch and freelancer:
            # Check if batch member record exists
            batch_member = BatchMember.query.filter_by(batch_id=batch_id, manager_id=batch.created_by).first()
            username = freelancer.username  # store only username

            if batch_member:
                members = batch_member.team_members.split(",") if batch_member.team_members else []
                if username not in members:
                    members.append(username)
                batch_member.team_members = ",".join(members)
            else:
                batch_member = BatchMember(
                    batch_id=batch.id,
                    project_id=batch.job_id,
                    manager_id=batch.created_by,
                    team_members=username
                )
                db.session.add(batch_member)

            db.session.commit()

    return app_obj.to_dict() if app_obj else None




# def change_application_status(application_id, status):
#     app = update_application_status(application_id, status)
#     return app.to_dict() if app else None


