# app/repositories/batch_repository.py
from app.models.batch import Batch
from app import db

def create_batch(project_id, project_name, project_type, count, created_by):
    batch = Batch(
        project_id=project_id,
        project_name=project_name,
        project_type=project_type,
        count=count,
        created_by=created_by
    )
    db.session.add(batch)
    db.session.commit()
    return batch

def get_batch_by_id(batch_id):
    return Batch.query.get(batch_id)

def get_batches_by_manager(manager_id):
    return Batch.query.filter_by(created_by=manager_id).all()
