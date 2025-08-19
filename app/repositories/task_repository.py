# app/repositories/task_repository.py
from app.models.task import Task
from app import db
from sqlalchemy.orm import joinedload

def create_task(batch_id, name, count, deadline, assign_date, extra_metadata, assigned_by, assigned_to=None):
    task = Task(
        batch_id=batch_id,
        name=name,
        count=count,
        deadline=deadline,
        assign_date=assign_date,
        extra_metadata=extra_metadata,
        assigned_by=assigned_by,
        assigned_to=assigned_to
    )
    db.session.add(task)
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
