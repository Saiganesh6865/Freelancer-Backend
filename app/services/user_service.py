from app.models.user import User
from app.models.password_reset_otp import PasswordResetOTP
from app.models.revoked_token import RevokedToken
from app.models import db
from datetime import datetime, timedelta, timezone
import random
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    decode_token
)

# ---------------- AUTHENTICATION ----------------
def generate_tokens(user):
    identity = str(user.id)
    claims = {"role": user.role}

    access_token = create_access_token(
        identity=identity,
        additional_claims=claims,
        expires_delta=timedelta(minutes=59)
    )

    refresh_token = create_refresh_token(
        identity=identity,
        additional_claims=claims,
        expires_delta=timedelta(days=7)
    )

    return access_token, refresh_token


def authenticate_and_generate_tokens(data):
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return {"error": "Email and password are required", "code": 422}

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return {"error": "Invalid credentials", "code": 401}

    access_token, refresh_token = generate_tokens(user)
    return {
        "user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role},
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def refresh_tokens():
    """
    Implements refresh token rotation with revocation.
    """
    user_id = get_jwt_identity()
    if not user_id:
        return {"error": "Invalid or missing user ID", "code": 401}

    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found", "code": 404}

    # Revoke old refresh token
    old_jti = get_jwt().get("jti")
    if old_jti:
        revoke_token_if_not_exists(old_jti)

    access_token, refresh_token = generate_tokens(user)
    return {
        "user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role},
        "access_token": access_token,
        "refresh_token": refresh_token
    }


# ---------------- TOKEN REVOCATION ----------------
def revoke_token_if_not_exists(jti):
    """
    Blacklist the token JTI if it does not already exist.
    """
    if not RevokedToken.query.filter_by(jti=jti).first():
        revoked = RevokedToken(jti=jti, revoked_at=datetime.now(timezone.utc))
        db.session.add(revoked)
        db.session.commit()
    return True


def logout_user(jwt_data):
    """
    Revoke the access token JTI.
    """
    jti = jwt_data.get("jti")
    if jti:
        revoke_token_if_not_exists(jti)
    return True


# ---------------- USER MANAGEMENT ----------------
def signup_user(total_users, data):
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")
    manager_type = data.get("manager_type")

    if not all([username, email, password, role]):
        return {"error": "Missing required fields", "code": 400}

    if total_users == 0 and role.lower() != "admin":
        return {"error": "First user must be an admin", "code": 403}

    existing = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing:
        return {"error": "Username or email already exists", "code": 400}

    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_pw, role=role)
    if role.lower() == "manager" and manager_type:
        new_user.manager_type = manager_type

    db.session.add(new_user)
    db.session.commit()
    return {
        "message": "User created successfully",
        "user": {"id": new_user.id, "username": new_user.username, "role": new_user.role},
        "status": 200
    }


def check_session_service(request):
    """
    Check access token validity; if expired, use refresh token to issue new access token.
    """
    from flask_jwt_extended import verify_jwt_in_request, create_access_token
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if not user_id:
            return {"error": "Invalid or missing user ID", "code": 401}

        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found", "code": 401}
        return {"user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role}}

    except Exception:
        refresh_token = request.cookies.get("refresh_token_cookie")
        if not refresh_token:
            return {"error": "Unauthorized", "code": 401}

        decoded = decode_token(refresh_token)
        if decoded.get("type") != "refresh":
            return {"error": "Invalid refresh token", "code": 401}

        user_id = decoded.get("sub")
        if not user_id:
            return {"error": "Invalid refresh token payload", "code": 401}

        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found", "code": 401}

        new_access_token = create_access_token(identity=user_id)
        return {
            "user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role},
            "new_access_token": new_access_token
        }


# ---------------- PASSWORD RESET ----------------
def forgot_password_service(email):
    user = User.query.filter_by(email=email).first()
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
    # send_email(user.email, "OTP", f"Your OTP is {otp_code}")
    return "OTP sent to your registered email"


def reset_password_service(email, otp, new_password):
    user = User.query.filter_by(email=email).first()
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


# ---------------- CRUD ----------------
def list_all_users_service():
    return [u.to_dict() for u in User.query.all()]


def get_user_by_id_service(user_id):
    if not user_id:
        return None
    user = User.query.get(user_id)
    return user.to_dict() if user else None


def delete_user_service(user_id):
    if not user_id:
        return False
    user = User.query.get(user_id)
    if not user:
        return False
    db.session.delete(user)
    db.session.commit()
    return True


def count_users_service():
    return User.query.count()
