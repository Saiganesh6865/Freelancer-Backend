from app.models.user import User
from app.models.password_reset_otp import PasswordResetOTP 
from app import db
import random
from datetime import datetime, timedelta, timezone
# from app.utils.email_util import send_email 
from app.repositories.user_repository import (
    get_user_by_email,
    get_user_by_id,
    get_all_users,
    delete_user_by_id,
)
from app.repositories.revoked_token_repository import (
    is_token_revoked,
    revoke_token_if_not_exists
)
from app.auth.auth_utils import generate_tokens
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import get_jwt_identity, get_jwt
from flask_jwt_extended import decode_token, create_access_token

def authenticate_and_generate_tokens(data):
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return {"error": "Email and password are required", "code": 422}

    user = get_user_by_email(email)
    if not user or not check_password_hash(user.password, password):
        return {"error": "Invalid credentials", "code": 401}

    access_token, refresh_token = generate_tokens(user)
    user_data = {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        },
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    return user_data


def refresh_tokens():
    identity = get_jwt_identity()
    user = get_user_by_id(identity)
    if not user:
        return {"error": "User not found", "code": 404}

    old_refresh_jti = get_jwt().get("jti")
    revoke_token_if_not_exists(old_refresh_jti)

    access_token, refresh_token = generate_tokens(user)
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        },
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def signup_user(total_users, data):
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not all([username, email, password, role]):
        return {"error": "Missing required fields", "code": 400}


    # If no users exist, only allow admin signup without token
    if total_users == 0:
        if role.lower() != 'admin':
            return {"error": "First user must be an admin", "code": 403}

        user, error = create_user(username, email, password, role)
        if error:
            return {"error": error, "code": 400}

        return {
            "message": "Admin user created successfully",
            "user": {"id": user.id, "username": user.username, "role": user.role},
            "status": 201
        }

    # For other signups, require admin token - checked in controller

    user, error = create_user(username, email, password, role)
    if error:
        return {"error": error, "code": 400}

    return {
        "message": "User created successfully",
        "user": {"id": user.id, "username": user.username, "role": user.role},
        "status": 200
    }


def create_user(username, email, password, role):
    existing = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing:
        return None, "Username or email already exists"

    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_pw, role=role)

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return None, str(e)

    return new_user, None



def check_session_service(request):
    from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, decode_token, create_access_token
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()

        if not user_id:
            return {"error": "No valid token found", "code": 401}

        user = get_user_by_id(user_id)
        if not user:
            return {"error": "User not found", "code": 401}

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }

        return {"user": user_data}

    except Exception:
        # Try refresh token flow
        refresh_token = request.cookies.get('refresh_token_cookie')
        if not refresh_token:
            return {"error": "Unauthorized", "code": 401}

        decoded = decode_token(refresh_token)
        if decoded.get("type") != "refresh":
            return {"error": "Invalid refresh token", "code": 401}

        user_id = decoded["sub"]
        user = get_user_by_id(user_id)
        if not user:
            return {"error": "User not found", "code": 401}

        new_access_token = create_access_token(identity=user_id)
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }

        return {"user": user_data, "new_access_token": new_access_token}


def logout_user(jwt):
    jti = jwt['jti']

    if is_token_revoked(jti):
        return {"message": "Token already revoked", "code": 409}

    revoke_token_if_not_exists(jti)
    return {"message": "Logged out successfully", "code": 200}



def forgot_password_service(email):
    user = get_user_by_email(email)
    if not user:
        return "If the email is registered, you will receive an OTP"

    otp_code = f"{random.randint(100000, 999999)}"
    expiry_time = datetime.now(timezone.utc) + timedelta(minutes=10)

    existing_otp = PasswordResetOTP.query.filter_by(user_id=user.id).first()
    if existing_otp:
        existing_otp.otp = otp_code
        existing_otp.expires_at = expiry_time
    else:
        new_otp = PasswordResetOTP(user_id=user.id, otp=otp_code, expires_at=expiry_time)
        db.session.add(new_otp)
    db.session.commit()

    # send_email(user.email, "Password Reset OTP", f"Your OTP is {otp_code}. It expires in 10 minutes.")
    return "OTP sent to your registered email"


def reset_password_service(email, otp, new_password):
    user = get_user_by_email(email)
    if not user:
        return False

    otp_record = PasswordResetOTP.query.filter_by(user_id=user.id, otp=otp).first()
    if not otp_record or otp_record.expires_at < datetime.now(timezone.utc):
        return False

    if check_password_hash(user.password, new_password):
        return "same_password"

    user.password = generate_password_hash(new_password)
    db.session.delete(otp_record)
    db.session.commit()
    return True



def list_all_users_service():
    users = get_all_users()
    return [user.to_dict() for user in users]


def get_user_by_id_service(user_id):
    user = get_user_by_id(user_id)
    return user.to_dict() if user else None


def delete_user_service(user_id):
    return delete_user_by_id(user_id)


def count_users_service():
    return User.query.count()




