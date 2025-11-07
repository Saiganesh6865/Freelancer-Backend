from app import db
from app.models.revoked_token import RevokedToken
from datetime import datetime, timezone

def is_token_revoked(jti: str) -> bool:
    return db.session.query(RevokedToken).filter_by(jti=jti).first() is not None

def revoke_token_if_not_exists(jti: str):
    """
    Blacklist the token JTI if it does not already exist.
    """
    if not RevokedToken.query.filter_by(jti=jti).first():
        revoked = RevokedToken(jti=jti, revoked_at=datetime.now(timezone.utc))
        db.session.add(revoked)
        db.session.commit()
    return True
