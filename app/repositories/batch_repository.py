from app.models.batch import Batch
from app import db
from app.models.BatchMember import BatchMember
from app.models.user import User
import json

def create_batch(job_id, project_name, project_type, count, created_by, skills_required=None):
    batch = Batch(
        job_id=job_id,  # ✅ match the model
        project_name=project_name,
        project_type=project_type,
        count=count,
        created_by=created_by,
        skills_required=skills_required
    )
    db.session.add(batch)
    db.session.commit()
    return batch


def get_batch_by_id(batch_id):
    return Batch.query.get(batch_id)

def get_batches_by_manager(manager_id):
    return Batch.query.filter_by(created_by=manager_id).all()


def add_freelancer_to_batch(batch_id, project_id, manager_id, freelancer_id):
    freelancer = User.query.get(freelancer_id)
    if not freelancer:
        raise ValueError("Freelancer not found")

    new_member = {"id": freelancer.id, "name": freelancer.username}  # use name if available

    batch_member = BatchMember.query.filter_by(batch_id=batch_id, manager_id=manager_id).first()
    if batch_member:
        members = json.loads(batch_member.team_members) if batch_member.team_members else []
        if not any(m["id"] == freelancer.id for m in members):
            members.append(new_member)
        batch_member.team_members = json.dumps(members)
    else:
        batch_member = BatchMember(
            batch_id=batch_id,
            project_id=project_id,
            manager_id=manager_id,
            team_members=json.dumps([new_member])
        )
        db.session.add(batch_member)

    db.session.commit()
    return batch_member.to_dict()


def get_batch_members(batch_id):
    batch_member = BatchMember.query.filter_by(batch_id=batch_id).first()
    if batch_member:
        return batch_member.to_dict()
    return {"team_members": []}