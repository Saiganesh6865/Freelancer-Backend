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


# def get_batch_members(batch_id):
#     batch_member = BatchMember.query.filter_by(batch_id=batch_id).first()
#     if batch_member:
#         return batch_member.to_dict()
#     return {"team_members": []}

def get_batch_members(batch_id):
    batch_member = BatchMember.query.filter_by(batch_id=batch_id).first()
    return {"team_members": batch_member.get_team_members() if batch_member else []}

def assign_freelancers_to_batch(manager_id, batch_id, freelancer_ids):
    """
    Assign freelancers to a batch if the logged-in manager owns the batch.
    Only unassigned freelancers are added.
    """
    batch = Batch.query.get(batch_id)
    if not batch:
        return {"success": False, "error": "Batch not found"}

    # Authorization check
    if int(batch.created_by) != int(manager_id):
        return {"success": False, "error": "Unauthorized manager"}

    # Fetch freelancer usernames
    freelancers = User.query.filter(User.id.in_(freelancer_ids), User.role=="freelancer").all()
    usernames_to_assign = [f.username for f in freelancers]

    # Check if BatchMember record exists
    batch_member = BatchMember.query.filter_by(batch_id=batch.id, manager_id=manager_id).first()
    if batch_member:
        current_members = batch_member.get_team_members()
        # Only add unassigned freelancers
        new_members = list(set(current_members + usernames_to_assign))
        batch_member.set_team_members(new_members)
    else:
        # Create new batch member record
        batch_member = BatchMember(
            batch_id=batch.id,
            project_id=batch.job_id,
            manager_id=manager_id,
            team_members=",".join(usernames_to_assign)
        )
        db.session.add(batch_member)

    db.session.commit()
    return {"success": True, "batch": batch_member.to_dict()}