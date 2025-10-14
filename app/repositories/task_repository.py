# app/repositories/task_repository.py
from app.models.task import Task
from app import db
from app.models.user import User
from sqlalchemy.orm import joinedload

# def create_task(batch_id, name, count, deadline, assign_date, assigned_by, assigned_to=None):
#     task = Task(
#         batch_id=batch_id,
#         name=name,
#         count=count,
#         deadline=deadline,
#         assign_date=assign_date,
#         assigned_by=assigned_by,
#         assigned_to=assigned_to
#     )
#     db.session.add(task)
#     db.session.commit()
#     return task

def create_task(data):
    # Find freelancer by username
    freelancer = User.query.filter_by(username=data["assigned_to_username"]).first()
    if not freelancer:
        raise ValueError("Freelancer not found")

    # Create task with freelancer.id
    task = Task(
        job_id=data["project_id"],
        batch_id=data["batch_id"],
        title=data["title"],
        description=data.get("description"),
        count=data.get("count", 0),
        status="pending",
        assigned_by=data["assigned_by"],
        assigned_to=freelancer.id
    )
    db.session.add(task)
    db.session.commit()

    # # Count how many tasks this freelancer has in this batch
    # task_count = Task.query.filter_by(batch_id=data["batch_id"], assigned_to=freelancer.id).count()

    return {
        "message": "Task assigned successfully",
        "task": {
            "task_id": task.id,
            "batch_id": task.batch_id,
            "member_id": freelancer.id,
            "username": freelancer.username,
            "title": task.title,
            "count": task.count,
            "status": task.status
        }
    }
def get_tasks_by_project(project_id):
    return Task.query.filter_by(project_id=project_id).all()

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
    # Fetch tasks for batches belonging to manager's projects
    from app.models.batch import Batch
    return Task.query.join(Batch, Task.batch_id == Batch.id)\
                     .filter(Batch.created_by == manager_id)\
                     .options(joinedload(Task.batch))\
                     .all()

def delete_tasks_by_batch(batch_id):
    Task.query.filter_by(batch_id=batch_id).delete()
    db.session.commit()
