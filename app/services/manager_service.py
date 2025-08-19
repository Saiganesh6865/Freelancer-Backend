from datetime import datetime
from app.repositories.project_repository import get_project_by_id, get_projects_by_manager
from app.repositories.batch_repository import create_batch, get_batches_by_manager, get_batch_by_id
from app.repositories.task_repository import create_task, get_tasks_by_manager
from app.repositories.manager_repository import fetch_dashboard_metrics, fetch_jobs_by_manager

# ---------- Manager: Dashboard metrics ----------
def get_manager_dashboard_data(manager_id):
    return fetch_dashboard_metrics(manager_id)

# ---------- Manager: Jobs ----------
def get_manager_jobs(manager_id):
    jobs = fetch_jobs_by_manager(manager_id)
    return [job.to_dict() for job in jobs]

# ---------- Manager: Projects ----------
def get_manager_projects(manager_id):
    projects = get_projects_by_manager(manager_id)
    return [proj.to_dict() for proj in projects]

# ---------- Manager: Tasks ----------
def get_manager_tasks(manager_id):
    tasks = get_tasks_by_manager(manager_id)
    return [task.to_dict() for task in tasks]

# ---------- Manager: Batches ----------
def get_manager_batches(manager_id):
    batches = get_batches_by_manager(manager_id)
    return [batch.to_dict() for batch in batches]

# ---------- Manager: Add batch ----------
def add_batch(manager_id, data):
    project = get_project_by_id(data["project_id"])
    if not project:
        raise ValueError("Invalid project_id")

    return create_batch(
        project_id=project.id,
        project_name=project.name,
        project_type=project.project_type,
        count=data.get("count", 0),
        created_by=manager_id
    )

# ---------- Manager: Add task ----------
def add_task(manager_id, data):
    batch = get_batch_by_id(data["batch_id"])
    if not batch:
        raise ValueError("Invalid batch_id")

    return create_task(
        batch_id=batch.id,
        name=data["name"],
        count=data.get("count", 1),
        deadline=datetime.strptime(data["deadline"], "%d-%m-%Y %H:%M:%S") if data.get("deadline") else None,
        assign_date=datetime.strptime(data["assign_date"], "%d-%m-%Y %H:%M:%S") if data.get("assign_date") else datetime.utcnow(),
        extra_metadata=data.get("metadata"),
        assigned_by=manager_id,
        assigned_to=data.get("assigned_to")
    )

# ---------- Manager: Task creation helper ----------
def create_task_for_project(manager_id, project_id, data):
    return add_task(manager_id, data)
