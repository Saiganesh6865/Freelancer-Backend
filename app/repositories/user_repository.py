from app.models.user import User
from flask_jwt_extended import get_jwt, verify_jwt_in_request, get_jwt_identity
from app import db
from werkzeug.security import generate_password_hash

def is_admin_request():
    try:
        verify_jwt_in_request()
        identity = get_jwt_identity()
        claims = get_jwt()
        print(f"User ID: {identity}, Role: {claims.get('role')}")
        return claims.get("role", "").lower() == "admin"
    except Exception as e:
        print("JWT Error:", str(e))
        return False

def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

def count_users():
    return User.query.count()

def get_all_users():
    return User.query.all()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def delete_user_by_id(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False

def update_user_by_id(user_id, data):
    user = User.query.get(user_id)
    if not user:
        return False

    if 'username' in data:
        user.username = data['username']
    if 'role' in data:
        user.role = data['role']
    if 'password' in data:
        user.password = generate_password_hash(data['password'])

    db.session.commit()
    return True


def is_manager_request():
    try:
        verify_jwt_in_request()
        claims = get_jwt()
        return claims.get("role", "").lower() == "manager"
    except Exception as e:
        print("JWT Error:", str(e))
        return False

def is_freelancer_request():
    try:
        verify_jwt_in_request()
        claims = get_jwt()
        return claims.get("role", "").lower() == "freelancer"
    except Exception:
        return False

# def is_admin_request():
#     try:
#         verify_jwt_in_request()
#         identity = get_jwt_identity()
#         return identity.get("role") == "admin"
#     except Exception:
#         return False