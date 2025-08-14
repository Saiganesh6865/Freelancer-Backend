from app.repositories.user_repository import count_users
from app.repositories.job_repository import count_total_jobs, count_completed_jobs
from app.repositories.job_repository import create_job
from app.repositories.task_repository import create_task
from datetime import datetime

def get_admin_stats():
    return {
        "total_users": count_users(),
        "total_jobs": count_total_jobs(),
        "completed_jobs": count_completed_jobs()
    }


def create_project_with_tasks(admin_id, data):
    job = create_job(
        title=data["title"],
        description=data["description"],
        project_type=data["project_type"],
        created_by=admin_id,
        skills_required=data.get("skills_required"),
        status="open"
    )

    for task in data.get("tasks", []):
        create_task(
            job_id=job.id,
            name=task["name"],
            count=task.get("count", 1),
            deadline=datetime.strptime(task["deadline"], "%d-%m-%Y %H:%M:%S"),
            extra_metadata=task.get("metadata")
        )

    return job