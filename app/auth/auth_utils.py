from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta

def generate_tokens(user):
    identity = str(user.id)
    claims = {"role": user.role}

    access_token = create_access_token(
        identity=identity,
        additional_claims=claims,
        expires_delta=timedelta(minutes=60)  # Access token 60 min
    )
    refresh_token = create_refresh_token(
        identity=identity,
        additional_claims=claims,
        expires_delta=timedelta(days=7)      # Refresh token 7 days
    )

    return access_token, refresh_token
