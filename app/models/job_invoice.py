from app import db

class JobInvoice(db.Model):
    __tablename__ = "job_invoices"

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.String(100), unique=True, nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    client_details = db.Column(db.String(255))
    issue_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    subtotal = db.Column(db.Float, default=0.0)
    total_due = db.Column(db.Float, default=0.0)
    project_type = db.Column(db.String(100))
    status = db.Column(db.String(50), default="Pending")  # Pending / Approved / Rejected
    created_by = db.Column(db.String(50))  # 'Freelancer' or 'Manager'
    created_user_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    items = db.relationship("JobInvoiceItem", backref="invoice", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "invoice_id": self.invoice_id,
            "job_id": self.job_id,
            "client_details": self.client_details,
            "issue_date": self.issue_date,
            "due_date": self.due_date,
            "subtotal": self.subtotal,
            "total_due": self.total_due,
            "project_type": self.project_type,
            "status": self.status,
            "created_by": self.created_by,
            "created_user_id": self.created_user_id,
            "created_at": self.created_at,
            "items": [item.to_dict() for item in self.items],
        }


class JobInvoiceItem(db.Model):
    __tablename__ = "job_invoice_items"

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("job_invoices.id", ondelete="CASCADE"))
    description = db.Column(db.String(255))
    rate = db.Column(db.Float)
    hours = db.Column(db.Float)
    count = db.Column(db.Float)
    amount = db.Column(db.Float)

    def to_dict(self):
        return {
            "description": self.description,
            "rate": self.rate,
            "hours": self.hours,
            "count": self.count,
            "amount": self.amount,
        }
