from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from app import db
import enum

class OnboardingStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Onboarding(db.Model):
    __tablename__ = "onboardings"

    id = Column(Integer, primary_key=True, index=True)
    freelancer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(Enum(OnboardingStatus), default=OnboardingStatus.PENDING)
    notes = Column(String, nullable=True)

    freelancer = relationship("User", back_populates="onboardings")
    job = relationship("Job", back_populates="onboardings")
