from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, verify_jwt_in_request
from datetime import timedelta


def generate_tokens(user):
    identity = str(user.id)
    claims = {"role": user.role}
    
    access_token = create_access_token(
        identity=identity,
        additional_claims=claims,
        expires_delta=timedelta(minutes=59)  # ⏰ Access token valid for 20 min
    )
    refresh_token = create_refresh_token(
        identity=identity,
        additional_claims=claims,
        expires_delta=timedelta(days=7)     # ⏳ Refresh token valid for 7 days
    )
    
    return access_token, refresh_token

# ✅ Add this function to get current manager id from JWT
def get_current_manager_id():
    """
    Returns the logged-in manager's user ID from the JWT.
    Must be called inside a Flask route protected with @jwt_required()
    """
    verify_jwt_in_request()
    return int(get_jwt_identity())