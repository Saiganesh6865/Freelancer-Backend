from datetime import datetime
from dateutil import parser
from app.repositories.batch_repository import create_batch, get_batch_by_id, assign_freelancers_to_batch, update_batch, get_batch_members
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
from sqlalchemy.exc import SQLAlchemyError



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
            "project_type": job.project_type,
            "created_at": job.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for job in jobs
    ]


# ---------- Tasks ----------
def get_manager_tasks(manager_id, job_id=None):
    from app.models.task import Task

    query = db.session.query(Task).join(Job, Job.id == Task.job_id).filter(Job.manager_id == manager_id)
    if job_id:
        query = query.filter(Task.job_id == job_id)

    tasks = query.all()
    return [t.to_dict(include_job=True, include_batch=True, include_freelancer=True) for t in tasks]


def create_task_for_job(manager_id, data):
    """
    Wrapper to create a task with assigned_by injected.
    """
    data["assigned_by"] = manager_id
    return create_task(data)


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
def add_batch(manager_id, data):
    job_id = data.get("job_id") or data.get("project_id")
    job = Job.query.get(job_id)
    if not job or int(job.manager_id) != int(manager_id):
        raise ValueError("Invalid job_id or unauthorized manager")

    # Parse deadline from frontend
    deadline_str = data.get("deadline")
    deadline_dt = None
    if deadline_str:
        try:
            deadline_dt = parser.isoparse(deadline_str)  # Converts ISO string to datetime
        except Exception:
            raise ValueError("Invalid deadline format. Use YYYY-MM-DD or ISO format.")

    return create_batch(
        job_id=job.id,
        project_name=job.title,
        project_type=job.project_type if hasattr(job, "project_type") else data.get("project_type"),
        count=data.get("count", 0),
        created_by=manager_id,
        skills_required=job.skills_required,
        deadline=deadline_dt
    ).to_dict()

def get_manager_batches(manager_id):
    batches = Batch.query.filter_by(created_by=manager_id).all()
    result = []

    from app.models.task import Task

    for batch in batches:
        batch_member = BatchMember.query.filter_by(batch_id=batch.id).first()
        members = []

        if batch_member and batch_member.team_members:
            # Convert comma-separated string to array of objects
            members = [
                {"id": idx + 1, "username": name.strip(), "assigned_count": 0}
                for idx, name in enumerate(batch_member.team_members.split(","))
            ]

        total_assigned = sum(t.count for t in Task.query.filter_by(batch_id=batch.id).all())
        total_assigned = min(total_assigned, batch.count)  # clamp to batch.count
        remaining_tasks = batch.count - total_assigned

        result.append({
            "id": batch.id,
            "job_id": batch.job_id,
            "project_name": batch.project_name,
            "project_type": batch.project_type,
            "count": batch.count,
            "skills_required": batch.skills_required,
            "team_members": members,  # <-- now always an array of objects
            "total_assigned": total_assigned,
            "remaining_tasks": remaining_tasks,
            "created_at": batch.created_at.isoformat() if batch.created_at else None
        })

    return result

# ---------- Freelancers ----------
def get_manager_freelancers(manager_id):
    freelancers = User.query.filter_by(role="freelancer").all()
    return [f.to_dict() for f in freelancers]


# ---------- Applications ----------
def get_batch_applications(manager_id, batch_id):
    batch = Batch.query.filter_by(id=batch_id).first()
    if not batch:
        return {"success": False, "error": "Batch not found"}

    if int(batch.created_by) != int(manager_id):
        return {"success": False, "error": "Batch not owned by this manager"}

    applications = Application.query.filter_by(batch_id=batch_id).all()
    return {
        "success": True,
        "batch": batch.to_dict(),
        "applications": [app.to_dict() for app in applications]
    }


def change_application_status(application_id, status):
    app_obj = update_application_status(application_id, status)
    if not app_obj:
        return None

    # Fetch batch to get manager_id safely
    batch = Batch.query.get(app_obj.batch_id)

    # Only assign when accepted
    if status == "accepted" and batch:
        assign_freelancers_to_batch(
            manager_id=batch.created_by,
            batch_id=batch.id,
            freelancer_ids=[app_obj.freelancer_id],
        )

    # Return safe dict (remove manager_id issues)
    return {
        "id": app_obj.id,
        "freelancer_id": app_obj.freelancer_id,
        "batch_id": app_obj.batch_id,
        "status": app_obj.status,
        "applied_at": app_obj.applied_at.isoformat() if app_obj.applied_at else None,
        "updated_at": app_obj.updated_at.isoformat() if app_obj.updated_at else None,
    }



#---------------------------edit batches------------------

def edit_batch(manager_id, batch_id, data):
    batch = get_batch_by_id(batch_id)
    if not batch:
        return {"success": False, "error": "Batch not found"}, 404

    if int(batch.created_by) != int(manager_id):
        return {"success": False, "error": "Unauthorized"}, 403

    editable_fields = ["count", "deadline", "skills_required", "project_type"]
    for field in editable_fields:
        if field in data:
            if field == "deadline":
                try:
                    # First try ISO parse
                    batch.deadline = parser.isoparse(data[field])
                except Exception:
                    try:
                        # Fallback for YYYY-MM-DD format
                        batch.deadline = datetime.strptime(data[field], "%Y-%m-%d")
                    except Exception:
                        return {"success": False, "error": "Invalid deadline format"}, 400
            else:
                setattr(batch, field, data[field])

    try:
        db.session.commit()
        return {"success": True, "batch": batch.to_dict()}
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500
