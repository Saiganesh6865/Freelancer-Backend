from app import db
from app.models.revoked_token import RevokedToken
from datetime import datetime, timezone

def is_token_revoked(jti: str) -> bool:
    return db.session.query(RevokedToken).filter_by(jti=jti).first() is not None

def revoke_token_if_not_exists(jti: str):
    if not is_token_revoked(jti):
        revoked_token = RevokedToken(jti=jti, revoked_at=datetime.now(timezone.utc))
        db.session.add(revoked_token)
        db.session.commit()
