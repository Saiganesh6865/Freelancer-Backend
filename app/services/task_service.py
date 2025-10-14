from app.repositories import task_repository

def assign_task(data):
    return task_repository.create_task(data)

def fetch_project_tasks(project_id):
    return task_repository.get_tasks_by_project(project_id)

def fetch_user_tasks(user_id):
    return task_repository.get_tasks_by_user_id(user_id)

def change_task_status(task_id, status):
    return task_repository.update_task_status(task_id, status)
