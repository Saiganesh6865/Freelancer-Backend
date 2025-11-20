from app import db
from app.models.job_invoice import JobInvoice, JobInvoiceItem
from app.models import Job, Task


def create_invoice(data):
    invoice = JobInvoice(
        invoice_id=data["invoice_id"],
        job_id=data.get("job_id"),
        client_details=data["client_details"],
        issue_date=data["issue_date"],
        due_date=data["due_date"],
        subtotal=data["subtotal"],
        tax_amount=data["tax_amount"],
        total_due=data["total_due"],
    )
    db.session.add(invoice)
    db.session.flush()

    for item in data["line_items"]:
        db.session.add(JobInvoiceItem(
            invoice_id=invoice.id,
            description=item["description"],
            rate=item["rate"],
            hours=item["hours"],
            amount=item["amount"]
        ))
    db.session.commit()
    return invoice


def get_invoice_by_id(invoice_id):
    return JobInvoice.query.filter_by(invoice_id=invoice_id).first()


def get_all_invoices_by_manager(manager_id):
    return (
        JobInvoice.query
        .join(Job)
        .filter(Job.manager_id == manager_id)
        .order_by(JobInvoice.created_at.desc())
        .all()
    )


def get_freelancer_projects_with_work(freelancer_id, manager_id):
    """Fetch projects managed by the manager where the freelancer has assigned tasks."""
    return (
        Job.query
        .filter_by(manager_id=manager_id)
        .join(Task, Task.job_id == Job.id)
        .filter(Task.assigned_to == freelancer_id)  # ✅ updated
        .options(db.joinedload(Job.tasks))
        .all()
    )
