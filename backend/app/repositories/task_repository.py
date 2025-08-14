# app/repositories/task_repository.py
from app import db
from app.models.task import Task

def create_task(job_id, name, count, deadline, extra_metadata=None):
    task = Task(job_id=job_id, name=name, count=count, deadline=deadline, metadata=extra_metadata)
    db.session.add(task)
    db.session.commit()
    return task

def get_tasks_by_job(job_id):
    return Task.query.filter_by(job_id=job_id).all()

def delete_tasks_by_job(job_id):
    Task.query.filter_by(job_id=job_id).delete()
    db.session.commit()
