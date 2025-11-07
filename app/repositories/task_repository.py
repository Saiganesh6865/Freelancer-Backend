from app.models.task import Task
from app.models.batch import Batch
from app.models.BatchMember import BatchMember
from app.models.user import User
from app import db
import json
from sqlalchemy.exc import SQLAlchemyError


def safe_json_load(value):
    """
    Safely loads JSON data from a string.
    Returns [] if value is empty or invalid.
    """
    try:
        if not value:
            return []
        return json.loads(value)
    except (json.JSONDecodeError, TypeError, ValueError):
        return []


def create_task(data):
    """
    Creates a new task under a batch.
    Validates:
      - Required fields
      - Freelancer existence
      - Batch existence
      - Remaining task count
    Updates:
      - Task table
      - BatchMember assigned_count (JSON-safe)
    """
    # -----------------------------
    # 1️⃣  Extract and validate fields
    # -----------------------------
    batch_id = data.get("batch_id")
    job_id = data.get("job_id")
    manager_id = data.get("assigned_by")
    assigned_to_username = data.get("assigned_to_username")
    title = data.get("title")
    description = data.get("description")
    count = data.get("count")

    if not all([batch_id, job_id, manager_id, assigned_to_username, count, title]):
        raise ValueError("Missing required task fields")

    try:
        task_count = int(count)
    except ValueError:
        raise ValueError("Count must be an integer")

    if task_count <= 0:
        raise ValueError("Count must be greater than 0")

    # -----------------------------
    # 2️⃣  Validate freelancer and batch
    # -----------------------------
    freelancer = User.query.filter_by(username=assigned_to_username).first()
    if not freelancer:
        raise ValueError("Freelancer not found")
    assigned_to_id = freelancer.id

    batch = Batch.query.get(batch_id)
    if not batch:
        raise ValueError("Batch not found")

    # -----------------------------
    # 3️⃣  Check remaining available tasks
    # -----------------------------
    total_assigned = sum(int(t.count) for t in Task.query.filter_by(batch_id=batch_id).all())
    remaining_tasks = int(batch.count) - total_assigned
    if task_count > remaining_tasks:
        raise ValueError(f"Cannot assign more than remaining tasks ({remaining_tasks}) in this batch")

    # -----------------------------
    # 4️⃣  Create and add task
    # -----------------------------
    task = Task(
        job_id=job_id,
        batch_id=batch_id,
        title=title,
        description=description,
        count=task_count,
        status="pending",
        assigned_by=manager_id,
        assigned_to=assigned_to_id
    )
    db.session.add(task)

    # -----------------------------
    # 5️⃣  Update BatchMember JSON safely
    # -----------------------------
    batch_member = BatchMember.query.filter_by(batch_id=batch_id, manager_id=manager_id).first()

    current_members = safe_json_load(batch_member.team_members if batch_member else None)

    found = False
    for m in current_members:
        if m.get("id") == assigned_to_id:
            m["assigned_count"] = int(m.get("assigned_count", 0)) + task_count
            found = True
            break

    if not found:
        current_members.append({
            "id": assigned_to_id,
            "name": freelancer.username,
            "assigned_count": task_count
        })

    if batch_member:
        batch_member.team_members = json.dumps(current_members)
    else:
        batch_member = BatchMember(
            batch_id=batch_id,
            project_id=job_id,
            manager_id=manager_id,
            team_members=json.dumps(current_members)
        )
        db.session.add(batch_member)

    # -----------------------------
    # 6️⃣  Commit transaction safely
    # -----------------------------
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print("DB commit failed:", repr(e))
        raise ValueError("Database error while creating task")

    # -----------------------------
    # 7️⃣  Return task response
    # -----------------------------
    return task.to_dict(include_batch=True, include_freelancer=True)



def get_tasks_by_batch(batch_id):
    return Task.query.filter_by(batch_id=batch_id).all()


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


def get_tasks_by_manager(manager_id):
    from app.models.batch import Batch
    return Task.query.join(Batch, Task.batch_id == Batch.id)\
                     .filter(Batch.created_by == manager_id)\
                     .all()


def delete_tasks_by_batch(batch_id):
    Task.query.filter_by(batch_id=batch_id).delete()
    db.session.commit()


def get_task_by_id(task_id):
    return Task.query.get(task_id)

def update_task(task_id, data):
    task = get_task_by_id(task_id)
    if not task:
        return None

    editable_fields = ["title", "description", "count", "status", "assigned_to_username"]

    for field in editable_fields:
        if field in data:
            if field == "assigned_to_username":
                user = User.query.filter_by(username=data[field]).first()
                if not user:
                    raise ValueError("Assigned freelancer not found")
                task.assigned_to = user.id

            elif field == "count":
                try:
                    count_val = int(data[field])
                    if count_val <= 0:
                        raise ValueError("Count must be > 0")
                    total_assigned = sum(t.count for t in Task.query.filter_by(batch_id=task.batch_id).all()) - task.count
                    remaining_tasks = task.batch.count - total_assigned
                    if count_val > remaining_tasks:
                        raise ValueError(f"Cannot assign more than remaining tasks ({remaining_tasks})")
                    task.count = count_val
                except ValueError:
                    raise ValueError("Count must be integer")
            else:
                setattr(task, field, data[field])

    try:
        db.session.commit()
        return task
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e