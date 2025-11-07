from flask import Blueprint, request
from flask_jwt_extended import jwt_required, verify_jwt_in_request
from app.services import job_invoice_service
from app.repositories.user_repository import (
    is_manager_request,
    is_admin_request,
    is_freelancer_request,
)
from app.auth.auth_utils import (
    get_current_manager_id,
    get_current_freelancer_id,
    get_current_admin_id,
)
from app.utils.response import success_response, error_response


# ─────────────────────────────────────────────
# BLUEPRINTS FOR EACH ROLE
# ─────────────────────────────────────────────
freelancer_invoice_bp = Blueprint(
    "freelancer_invoice", __name__, url_prefix="/freelancer/invoices"
)
manager_invoice_bp = Blueprint(
    "manager_invoice", __name__, url_prefix="/manager/invoices"
)
admin_invoice_bp = Blueprint(
    "admin_invoice", __name__, url_prefix="/admin/invoices"
)


# ─────────────────────────────────────────────
# JWT SECURITY WRAPPER
# ─────────────────────────────────────────────
def secure_jwt_required(fn):
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return jwt_required()(wrapper)


# ─────────────────────────────────────────────
# FREELANCER ROUTES
# ─────────────────────────────────────────────
@freelancer_invoice_bp.route("/create", methods=["POST"])
@secure_jwt_required
def freelancer_create_invoice():
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    try:
        data = request.get_json(silent=True)
        freelancer_id = get_current_freelancer_id()
        
        # ✅ Fix: pass user info as dict
        user = {"id": freelancer_id, "role": "freelancer"}

        invoice = job_invoice_service.create_invoice(data, user)
        return success_response("Invoice created successfully", invoice)
    except Exception as e:
        print("❌ Freelancer create invoice error:", repr(e))
        return error_response("Internal server error", 500)



@freelancer_invoice_bp.route("/my", methods=["GET"])
@secure_jwt_required
def freelancer_my_invoices():
    """Freelancer views all their own invoices."""
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    try:
        freelancer_id = get_current_freelancer_id()
        invoices = job_invoice_service.get_invoices_for_freelancer(freelancer_id)

        return success_response("Invoices fetched successfully", invoices)
    except Exception as e:
        print("❌ Freelancer list invoices error:", repr(e))
        return error_response("Internal server error", 500)


# ─────────────────────────────────────────────
# FREELANCER WORK SUMMARY (auto user ID)
# ─────────────────────────────────────────────
@freelancer_invoice_bp.route("/work_summary", methods=["GET"])
@secure_jwt_required
def get_my_work_summary():
    """Freelancer fetches their own completed work summary."""
    if not is_freelancer_request():
        return error_response("Freelancers only", 403)

    try:
        freelancer_id = get_current_freelancer_id()
        print(f"🟢 Fetching work summary for freelancer_id={freelancer_id}")

        summary = job_invoice_service.get_freelancer_work_summary(freelancer_id)

        print(f"✅ Work summary fetched successfully. {len(summary)} projects found.")
        return success_response("Freelancer work summary fetched successfully", summary)
    except Exception as e:
        print("❌ Work summary error:", repr(e))
        return error_response("Internal server error", 500)


# ─────────────────────────────────────────────
# MANAGER ROUTES
# ─────────────────────────────────────────────
@manager_invoice_bp.route("/all", methods=["GET"])
@secure_jwt_required
def manager_all_invoices():
    """Manager views all invoices under their freelancers."""
    if not is_manager_request():
        return error_response("Managers only", 403)

    try:
        manager_id = get_current_manager_id()
        invoices = job_invoice_service.list_invoices(manager_id)
        return success_response("Invoices fetched successfully", invoices)
    except Exception as e:
        print("❌ Manager list invoices error:", repr(e))
        return error_response("Internal server error", 500)


@manager_invoice_bp.route("/<string:invoice_id>", methods=["GET"])
@secure_jwt_required
def manager_get_invoice(invoice_id):
    """Manager fetches a specific invoice by ID."""
    if not is_manager_request():
        return error_response("Managers only", 403)

    try:
        manager_id = get_current_manager_id()

        # Fetch the invoice details
        invoice = job_invoice_service.get_invoice_by_id_for_manager(invoice_id, manager_id)
        if not invoice:
            return error_response("Invoice not found or access denied", 404)

        return success_response("Invoice fetched successfully", invoice)
    except Exception as e:
        print("❌ Manager get invoice error:", repr(e))
        return error_response("Internal server error", 500)


@manager_invoice_bp.route("/<string:invoice_id>/status", methods=["PUT"])
@secure_jwt_required
def manager_update_invoice_status(invoice_id):
    """Manager approves or rejects an invoice."""
    if not is_manager_request():
        return error_response("Managers only", 403)

    try:
        data = request.get_json(silent=True)
        # Handle case where data is a string instead of dict
        if isinstance(data, str):
            import json
            data = json.loads(data)

        new_status = data.get("status") if isinstance(data, dict) else None
        if new_status not in ["Processed", "Rejected"]:
            return error_response("Invalid status value", 400)

        updated = job_invoice_service.update_invoice_status(invoice_id, new_status)
        if not updated:
            return error_response("Invoice not found", 404)

        return success_response(f"Invoice {new_status.lower()} successfully")
    except Exception as e:
        print("❌ Invoice status update error:", repr(e))
        return error_response("Internal server error", 500)


# ─────────────────────────────────────────────
# ADMIN ROUTES
# ─────────────────────────────────────────────
@admin_invoice_bp.route("/all", methods=["GET"])
@secure_jwt_required
def admin_all_invoices():
    """Admin can view all invoices in the system."""
    if not is_admin_request():
        return error_response("Admins only", 403)

    try:
        invoices = job_invoice_service.list_all_invoices()
        return success_response("All invoices fetched successfully", invoices)
    except Exception as e:
        print("❌ Admin list invoices error:", repr(e))
        return error_response("Internal server error", 500)
