from app.repositories.user_repository import count_users
from app import db
from app.models.job import Job

from app.models.user import User


def get_admin_stats():
    return {
        "total_users": count_users(),
        "total_projects": Job.query.count(),
        "completed_projects": Job.query.filter_by(status="completed").count()
    }


def create_project(admin_id, data):
    project = Job(
        title=data["title"],
        description=data.get("description"),
        description_file = data.get("description_file"),
        project_type=data["project_type"],
        skills_required=data.get("skills_required"),
        status="open",
        created_by=admin_id
    )
    db.session.add(project)
    db.session.commit()
    return project


def list_projects():
    projects = Job.query.all()
    return [p.to_dict() for p in projects]


def update_project(project_id, data):
    project = Job.query.get(project_id)
    if not project:
        raise Exception("Project not found")

    project.title = data.get("title", project.title)
    project.description = data.get("description", project.description)
    project.project_type = data.get("project_type", project.project_type)
    project.skills_required = data.get("skills_required", project.skills_required)
    project.status = data.get("status", project.status)

    db.session.commit()
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
    db.session.commit()
    return project


def close_project(project_id):
    project = Job.query.get(project_id)
    if not project:
        raise Exception("Project not found")

    project.status = "completed"
    db.session.commit()
    return project



def assign_manager_to_jobs(job_ids, manager_username):
    from app.models.job import Job
    from app.models.user import User
    from app import db

    # Fetch manager by username
    manager = User.query.filter_by(username=manager_username).first()
    if not manager or manager.role != "manager":
        return {"message": "Invalid manager username"}, 400

    assigned_jobs = []
    not_found_jobs = []

    for job_id in job_ids:
        job = Job.query.get(job_id)
        if not job:
            not_found_jobs.append(job_id)
            continue

        # Assign manager
        job.manager_id = manager.id
        assigned_jobs.append(job.to_dict())

    db.session.commit()

    return {
        "message": f"Manager {manager.username} assigned to {len(assigned_jobs)} jobs",
        "assigned_jobs": assigned_jobs,
        "not_found_jobs": not_found_jobs
    }, 200

