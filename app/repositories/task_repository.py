from app.models.task import Task
from app import db
from app.models.user import User

def create_task(data):
    """
    Creates a task assigned to a freelancer.
    Expects data:
    - job_id
    - batch_id
    - title
    - description (optional)
    - count (optional)
    - assigned_by
    - assigned_to_username (optional)
    """
    # Find freelancer by username if provided
    assigned_to_id = None
    if data.get("assigned_to_username"):
        freelancer = User.query.filter_by(username=data["assigned_to_username"]).first()
        if not freelancer:
            raise ValueError("Freelancer not found")
        assigned_to_id = freelancer.id

    # Create task
    task = Task(
        job_id=data["job_id"],          # required
        batch_id=data["batch_id"],      # required
        title=data["title"],            # required
        description=data.get("description"),
        count=data.get("count", 0),
        status="pending",
        assigned_by=data["assigned_by"],
        assigned_to=assigned_to_id
    )
    db.session.add(task)
    db.session.commit()

    return {
        "message": "Task assigned successfully",
        "task": {
            "task_id": task.id,
            "batch_id": task.batch_id,
            "member_id": assigned_to_id,
            "username": data.get("assigned_to_username"),
            "title": task.title,
            "count": task.count,
            "status": task.status
        }
    }

# --- Other repository functions ---
def get_tasks_by_job(job_id):
    return Task.query.filter_by(job_id=job_id).all()

def get_tasks_by_user_id(user_id):
    return Task.query.filter_by(assigned_to=user_id).all()

def update_task_status(task_id, status):
    task = Task.query.get(task_id)
    if task:
        task.status = status
        db.session.commit()
    return task

def get_tasks_by_batch(batch_id):
    return Task.query.filter_by(batch_id=batch_id).all()

def get_tasks_by_manager(manager_id):
    from app.models.batch import Batch
    return Task.query.join(Batch, Task.batch_id == Batch.id)\
                     .filter(Batch.created_by == manager_id)\
                     .all()

def delete_tasks_by_batch(batch_id):
    Task.query.filter_by(batch_id=batch_id).delete()
    db.session.commit()
