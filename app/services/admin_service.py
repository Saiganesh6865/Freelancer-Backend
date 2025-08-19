from app.repositories.user_repository import count_users
from app.repositories.job_repository import (
    count_total_jobs,
    count_completed_jobs,
    create_job,
    fetch_all_jobs,
    save_job,
)
from app import db
from app.models.job import Job

def get_admin_stats():
    return {
        "total_users": count_users(),
        "total_jobs": count_total_jobs(),
        "completed_jobs": count_completed_jobs()
    }

def create_project(admin_id, data):
    job = create_job(
        title=data["title"],
        description=data["description"],
        project_type=data["project_type"],
        created_by=admin_id,
        skills_required=data.get("skills_required"),
        status="open",
    )
    return job

def list_projects():
    projects = fetch_all_jobs()
    return [project.to_dict() for project in projects]

def update_project(project_id, data):
    project = Job.query.get(project_id)
    if not project:
        raise Exception("Project not found")

    # Update allowed fields
    project.title = data.get("title", project.title)
    project.description = data.get("description", project.description)
    project.project_type = data.get("project_type", project.project_type)
    project.skills_required = data.get("skills_required", project.skills_required)
    project.status = data.get("status", project.status)

    save_job(project)
    return project

def delete_project(project_id):
    project = Job.query.get(project_id)
    if not project:
        raise Exception("Project not found")

    db.session.delete(project)
    db.session.commit()
    return True


def assign_manager(project_id, manager_id):
    project = Job.query.get(project_id)
    if not project:
        raise Exception("Project not found")

    project.manager_id = manager_id
    save_job(project)
    return project

def close_project(project_id):
    project = Job.query.get(project_id)
    if not project:
        raise Exception("Project not found")

    project.status = "completed"  # or "closed" depending on your convention
    save_job(project)
    return project

