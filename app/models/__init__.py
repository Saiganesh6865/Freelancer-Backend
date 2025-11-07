from app import db
from .user import User
from .job import Job
from .application import Application
from .freelancer_profile import FreelancerProfile
from .onboarding_model import Onboarding
from .revoked_token import RevokedToken
from .password_reset_otp import PasswordResetOTP
from .batch import Batch
from .task import Task
from .job_invoice import JobInvoice, JobInvoiceItem  # ✅ include both

__all__ = [
    "db",
    "User",
    "Job",
    "Application",
    "FreelancerProfile",
    "Onboarding",
    "RevokedToken",
    "PasswordResetOTP",
    "Batch",
    "Task",
    "JobInvoice",
    "JobInvoiceItem"  # ✅ add here too
]
