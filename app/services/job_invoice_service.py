from datetime import datetime
from app.models import JobInvoice, JobInvoiceItem, Job, Task
from app import db


# ───────────────────────────────
#  CREATE INVOICE
# ───────────────────────────────
def create_invoice(data, user):
    try:
        project_id = data.get("project_id")
        line_items = data.get("line_items", [])
        client_details = data.get("client_details", "")
        issue_date = data.get("issue_date")
        due_date = data.get("due_date")

        if not project_id or not line_items:
            raise ValueError("Missing project_id or line items.")

        issue_date = (
            datetime.strptime(issue_date, "%Y-%m-%d").date()
            if issue_date
            else datetime.utcnow().date()
        )
        due_date = (
            datetime.strptime(due_date, "%Y-%m-%d").date()
            if due_date
            else None
        )

        project = Job.query.get(project_id)
        if not project:
            raise ValueError("Invalid project_id: Project not found.")

        project_type = project.project_type.lower().strip() if project.project_type else "general"
        subtotal = 0
        invoice_items = []

        for item in line_items:
            rate = float(item.get("rate", 0))
            hours = float(item.get("hours", 0))
            count = float(item.get("count", 0))
            amount = rate * (count if project_type == "annotation" else hours)
            subtotal += amount

            invoice_items.append(
                JobInvoiceItem(
                    description=item.get("description", ""),
                    rate=rate,
                    hours=hours if project_type != "annotation" else 0,
                    count=count if project_type == "annotation" else 0,
                    amount=amount,
                )
            )

        total = round(subtotal, 2)
        generated_invoice_id = f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        invoice = JobInvoice(
            invoice_id=generated_invoice_id,
            job_id=project_id,
            client_details=client_details,
            project_type=project_type,
            issue_date=issue_date,
            due_date=due_date,
            subtotal=subtotal,
            total_due=total,
            status="Pending",
            created_by=user["role"],
            created_user_id=user["id"],
        )

        db.session.add(invoice)
        db.session.flush()

        for inv_item in invoice_items:
            inv_item.invoice_id = invoice.id
            db.session.add(inv_item)

        db.session.commit()
        return invoice.to_dict()

    except Exception as e:
        db.session.rollback()
        print("❌ Error creating invoice:", repr(e))
        raise


# ───────────────────────────────
#  FREELANCER FUNCTIONS
# ───────────────────────────────
def get_invoices_for_freelancer(user_id):
    invoices = (
        JobInvoice.query.filter_by(created_user_id=user_id)
        .order_by(JobInvoice.created_at.desc())
        .all()
    )
    return [inv.to_dict() for inv in invoices]


def get_freelancer_work_summary(freelancer_id):
    try:
        projects = (
            Job.query.join(Task)
            .filter(Task.assigned_to == freelancer_id)
            .distinct()
            .all()
        )

        summary = []
        for project in projects:
            task_list = []
            total_units = 0
            total_amount = 0
            project_type = project.project_type or "general"

            for task in project.tasks:
                if task.assigned_to != freelancer_id or task.status.lower() != "completed":
                    continue

                rate = float(getattr(task, "rate", 0) or 0)
                if project_type.lower() == "annotation":
                    count = int(getattr(task, "count", 0) or 0)
                    amount = count * rate
                    total_units += count
                else:
                    hours = float(getattr(task, "hours", 0) or 0)
                    amount = hours * rate
                    total_units += hours

                total_amount += amount
                task_list.append({
                    "task_id": task.id,
                    "task_title": task.title,
                    "description": task.description,
                    "hours": getattr(task, "hours", 0),
                    "count": getattr(task, "count", 0),
                    "rate": rate,
                    "amount": round(amount, 2),
                    "status": task.status,
                })

            if task_list:
                summary.append({
                    "project_id": project.id,
                    "project_title": project.title,
                    "project_type": project_type,
                    "tasks": task_list,
                    "total_units": total_units,
                    "total_amount": round(total_amount, 2),
                })

        return summary

    except Exception as e:
        print("❌ Work summary error:", repr(e))
        raise


# ───────────────────────────────
#  MANAGER FUNCTIONS
# ───────────────────────────────
def list_invoices(manager_id):
    """List all invoices belonging to projects managed by this manager."""
    invoices = (
        JobInvoice.query
        .join(Job, Job.id == JobInvoice.job_id)
        .filter(Job.manager_id == manager_id)
        .order_by(JobInvoice.created_at.desc())
        .all()
    )
    return [inv.to_dict() for inv in invoices]


def get_invoice_by_id_for_manager(invoice_id, manager_id):
    """Fetch a single invoice belonging to manager’s projects."""
    invoice = (
        JobInvoice.query
        .join(Job, Job.id == JobInvoice.job_id)
        .filter(JobInvoice.invoice_id == invoice_id)
        .filter(Job.manager_id == manager_id)
        .first()
    )

    if not invoice:
        print(f"⚠️ Invoice {invoice_id} not found or not owned by manager {manager_id}")
        return None

    return invoice.to_dict()


def update_invoice_status(invoice_id, new_status):
    """Manager updates invoice status."""
    invoice = JobInvoice.query.filter_by(invoice_id=invoice_id).first()
    if not invoice:
        return None
    invoice.status = new_status
    db.session.commit()
    return invoice.to_dict()


# ───────────────────────────────
#  ADMIN FUNCTIONS
# ───────────────────────────────
def list_all_invoices():
    invoices = JobInvoice.query.order_by(JobInvoice.created_at.desc()).all()
    return [inv.to_dict() for inv in invoices]
