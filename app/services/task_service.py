from app.repositories import task_repository
from app.models.job import Job
from app.repositories.task_repository import get_task_by_id, update_task

def assign_task(data):
    return task_repository.create_task(data)

def fetch_project_tasks(project_id):
    return task_repository.get_tasks_by_project(project_id)

def fetch_user_tasks(user_id):
    return task_repository.get_tasks_by_user_id(user_id)

def change_task_status(task_id, status):
    return task_repository.update_task_status(task_id, status)


def edit_task(manager_id, task_id, data):
    task = get_task_by_id(task_id)
    if not task:
        raise ValueError("Task not found")

    job = Job.query.get(task.job_id)
    if not job or job.manager_id != manager_id:
        raise PermissionError("Unauthorized")

    updated_task = update_task(task_id, data)
    return updated_task.to_dict(include_batch=True, include_freelancer=True)