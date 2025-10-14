from sqlalchemy.orm import Session
from app.models.onboarding_model import Onboarding, OnboardingStatus

def create_onboarding(db: Session, freelancer_id: int, job_id: int, start_date=None, end_date=None, notes=None):
    onboarding = Onboarding(
        freelancer_id=freelancer_id,
        job_id=job_id,
        start_date=start_date,
        end_date=end_date,
        notes=notes,
        status=OnboardingStatus.PENDING
    )
    db.add(onboarding)
    db.commit()
    db.refresh(onboarding)
    return onboarding

def get_onboarding_by_id(db: Session, onboarding_id: int):
    return db.query(Onboarding).filter(Onboarding.id == onboarding_id).first()

def get_onboarding_by_freelancer_id(db: Session, freelancer_id: int):
    return db.query(Onboarding).filter(Onboarding.freelancer_id == freelancer_id).all()

def get_all_onboardings(db: Session):
    return db.query(Onboarding).all()

def update_onboarding_status(db: Session, onboarding_id: int, new_status: OnboardingStatus):
    onboarding = db.query(Onboarding).filter(Onboarding.id == onboarding_id).first()
    if onboarding:
        onboarding.status = new_status
        db.commit()
        db.refresh(onboarding)
    return onboarding

def delete_onboarding(db: Session, onboarding_id: int):
    onboarding = db.query(Onboarding).filter(Onboarding.id == onboarding_id).first()
    if onboarding:
        db.delete(onboarding)
        db.commit()
    return onboarding
