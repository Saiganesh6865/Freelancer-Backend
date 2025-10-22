from app.models.batch import Batch
from app import db
from app.models.BatchMember import BatchMember
from app.models.user import User
import json
from sqlalchemy.exc import SQLAlchemyError
from dateutil import parser


# ---------------- Batch CRUD ----------------

def create_batch(job_id, project_name, project_type, count, created_by, skills_required=None, deadline=None):
    batch = Batch(
        job_id=job_id,
        project_name=project_name,
        project_type=project_type,
        count=count,
        created_by=created_by,
        skills_required=skills_required,
        deadline=deadline
    )
    db.session.add(batch)
    db.session.commit()
    return batch

def get_batch_by_id(batch_id):
    return Batch.query.get(batch_id)

from datetime import datetime
from dateutil import parser

def update_batch(batch_id, data):
    batch = get_batch_by_id(batch_id)
    if not batch:
        return None

    editable_fields = ["count", "deadline", "skills_required", "project_type"]
    for field in editable_fields:
        if field in data:
            if field == "deadline":
                try:
                    # First try ISO parse
                    batch.deadline = parser.isoparse(data[field])
                except Exception:
                    try:
                        # Fallback for YYYY-MM-DD format
                        batch.deadline = datetime.strptime(data[field], "%Y-%m-%d")
                    except Exception:
                        raise ValueError("Invalid deadline format. Use YYYY-MM-DD or ISO format.")
            else:
                setattr(batch, field, data[field])

    try:
        db.session.commit()
        return batch
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e



# ---------------- Batch Members ----------------

# def get_batch_members(batch_id):
#     batch_member = BatchMember.query.filter_by(batch_id=batch_id).first()
#     return {"team_members": batch_member.get_team_members() if batch_member else []}

def get_batch_members(batch_id):
    """
    Returns combined team members for a batch, handling both JSON and CSV formats.
    """
    batch_members_rows = BatchMember.query.filter_by(batch_id=batch_id).all()
    all_members = []

    for bm in batch_members_rows:
        if not bm.team_members:
            continue
        try:
            # Try parsing as JSON first
            members = json.loads(bm.team_members)
            all_members += members
        except Exception:
            # Fallback: comma-separated string
            names = [name.strip() for name in bm.team_members.split(",") if name.strip()]
            for idx, name in enumerate(names, start=1):
                all_members.append({"id": 0, "name": name})

    # Remove duplicates by freelancer name
    unique_members = {m['name']: m for m in all_members}.values()
    # Convert to comma-separated string
    team_members_str = ",".join([m["name"] for m in unique_members])

    return {"team_members": team_members_str}


# ---------------- Assign Freelancers ----------------

def assign_freelancers_to_batch(manager_id, batch_id, freelancer_ids):
    batch = Batch.query.get(batch_id)
    if not batch:
        return {"success": False, "error": "Batch not found"}
    if int(batch.created_by) != int(manager_id):
        return {"success": False, "error": "Unauthorized manager"}

    # Fetch freelancers
    freelancers = User.query.filter(User.id.in_(freelancer_ids), User.role=="freelancer").all()

    # Get or create BatchMember for this manager
    batch_member = BatchMember.query.filter_by(batch_id=batch.id, manager_id=manager_id).first()
    current_members = batch_member.get_team_members() if batch_member else []

    # Convert current members to dict for quick lookup
    member_dict = {m["id"]: m for m in current_members}

    # Add new freelancers without duplicates
    for f in freelancers:
        if f.id not in member_dict:
            member_dict[f.id] = {"id": f.id, "name": f.username}

    updated_members = list(member_dict.values())

    if batch_member:
        batch_member.set_team_members(updated_members)
    else:
        batch_member = BatchMember(
            batch_id=batch.id,
            project_id=batch.job_id,
            manager_id=manager_id,
            team_members=json.dumps(updated_members)
        )
        db.session.add(batch_member)

    db.session.commit()

    # Return combined members from all managers for this batch
    all_batch_members = BatchMember.query.filter_by(batch_id=batch.id).all()
    combined_members = []
    for bm in all_batch_members:
        combined_members += bm.get_team_members() if bm.team_members else []

    # Remove duplicates across managers
    unique_members = {m["id"]: m for m in combined_members}.values()
    simplified_members = [{"id": m["id"], "name": m["name"]} for m in unique_members]

    return {"success": True, "freelancers": simplified_members}


# ---------------- Get Batches by Manager ----------------

def get_batches_by_manager(manager_id):
    """
    Returns all batches created by the manager, with combined team members from all managers.
    """
    batches = Batch.query.filter_by(created_by=manager_id).all()
    result = []

    for batch in batches:
        batch_members_rows = BatchMember.query.filter_by(batch_id=batch.id).all()
        all_members = []

        for bm in batch_members_rows:
            if not bm.team_members:
                continue
            try:
                # Try parsing as JSON first
                members = json.loads(bm.team_members)
                all_members += members
            except Exception:
                # Fallback: comma-separated string
                names = [name.strip() for name in bm.team_members.split(",") if name.strip()]
                for idx, name in enumerate(names, start=1):
                    all_members.append({"id": 0, "name": name})

        # Remove duplicates by freelancer name
        unique_members = {m['name']: m for m in all_members}.values()
        team_members_str = ",".join([m["name"] for m in unique_members])

        result.append({
            "id": batch.id,
            "job_id": batch.job_id,
            "project_name": batch.project_name,
            "project_type": batch.project_type,
            "skills_required": batch.skills_required,
            "deadline": batch.deadline.isoformat() if batch.deadline else None,
            "created_at": batch.created_at.isoformat() if batch.created_at else None,
            "count": batch.count,
            "team_members": team_members_str
        })

    return result

