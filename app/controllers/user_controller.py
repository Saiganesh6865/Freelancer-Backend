import uuid
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import (
    jwt_required, set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies, verify_jwt_in_request, get_jwt, get_csrf_token,
    decode_token
)
from app.services.user_service import (
    authenticate_and_generate_tokens,
    refresh_tokens,
    signup_user,
    check_session_service,
    logout_user,
    list_all_users_service,
    get_user_by_id_service,
    delete_user_service,
    count_users_service,
    reset_password_service,
    forgot_password_service
)
from app.repositories.user_repository import is_admin_request, list_all_managers_service
from app.repositories.revoked_token_repository import revoke_token_if_not_exists
from app.utils.response import error_response

bp = Blueprint('user', __name__, url_prefix='/user')
COMPANY_EMAIL_DOMAIN = "@company.com"

# ---------- LOGIN ----------
@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 422

    result = authenticate_and_generate_tokens(data)
    if "error" in result:
        return jsonify({"error": result["error"]}), result.get("code", 401)

    access_token = result["access_token"]
    refresh_token = result["refresh_token"]
    csrf_token = get_csrf_token(access_token)

    response = make_response(jsonify({"user": result["user"], "csrf_token": csrf_token}))
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    response.set_cookie("csrf_access_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    response.set_cookie("csrf_refresh_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    return response, 200

# ---------- CSRF TOKEN ----------
@bp.route("/csrf-token", methods=["GET"])
def get_csrf_token_route():
    try:
        verify_jwt_in_request(optional=True)
        access_token = get_jwt().get("jti")
    except:
        access_token = None

    csrf_token = get_csrf_token(access_token) if access_token else str(uuid.uuid4())
    response = jsonify({"csrf_token": csrf_token})
    response.set_cookie("csrf_access_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    response.set_cookie("csrf_refresh_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    return response, 200

# ---------- REFRESH ----------
@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    result = refresh_tokens()
    if "error" in result:
        return jsonify({"error": result["error"]}), result.get("code", 401)

    access_token = result["access_token"]
    refresh_token = result["refresh_token"]
    csrf_token = get_csrf_token(access_token)

    response = make_response(jsonify({"user": result["user"], "csrf_token": csrf_token}))
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    response.set_cookie("csrf_access_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    response.set_cookie("csrf_refresh_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    return response, 200

# ---------- SESSION CHECK ----------
@bp.route('/session', methods=['GET'])
def check_session():
    result = check_session_service(request)
    if "error" in result:
        return jsonify({"error": result["error"]}), result.get("code", 401)

    token_for_csrf = result.get("new_access_token") or request.cookies.get("access_token_cookie")
    csrf_token = get_csrf_token(token_for_csrf) if token_for_csrf else str(uuid.uuid4())

    response = jsonify({"user": result["user"], "csrf_token": csrf_token})
    if "new_access_token" in result:
        set_access_cookies(response, result["new_access_token"])
    response.set_cookie("csrf_access_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    response.set_cookie("csrf_refresh_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    return response, 200

# ---------- CREATE FIRST ADMIN ----------
@bp.route('/create-admin', methods=['POST'])
def create_admin():
    total_users = count_users_service()
    if total_users > 0:
        return error_response("Admin already exists. Use regular signup with admin authorization.", 403)

    data = request.get_json()
    if not data:
        return error_response("Missing JSON body", 422)

    data["role"] = "admin"
    result = signup_user(total_users, data)
    if "error" in result:
        return error_response(result["error"], result.get("code", 400))

    return jsonify({"success": True, "message": "Admin created successfully", "user": result.get("user")}), 201

# ---------- SIGNUP ----------
@bp.route('/signup', methods=['POST'])
@jwt_required()
def signup():
    data = request.get_json()
    if not data:
        return error_response("Missing JSON body", 422)

    total_users = count_users_service()
    if total_users == 0:
        return error_response("Admin not created yet. Use /create-admin first.", 403)

    if not is_admin_request():
        return error_response("Only admin can create new users", 403)

    result = signup_user(total_users, data)
    if "error" in result:
        return error_response(result["error"], result.get("code", 400))

    csrf_token = get_csrf_token(get_jwt())
    response = jsonify(result)
    response.set_cookie("csrf_access_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    response.set_cookie("csrf_refresh_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    return response, result.get("status", 200)

# ---------- LOGOUT ----------
@bp.route("/logout", methods=["POST"])
def logout():
    """
    Revoke both access and refresh tokens and clear cookies
    """
    from flask_jwt_extended import verify_jwt_in_request, get_jwt
    # Revoke access token
    try:
        verify_jwt_in_request(optional=True)
        jwt_data = get_jwt()
        if jwt_data and jwt_data.get("jti"):
            revoke_token_if_not_exists(jwt_data["jti"])
    except Exception:
        pass

    # Revoke refresh token
    refresh_token = request.cookies.get("refresh_token_cookie")
    if refresh_token:
        try:
            decoded_refresh = decode_token(refresh_token)
            refresh_jti = decoded_refresh.get("jti")
            if refresh_jti:
                revoke_token_if_not_exists(refresh_jti)
        except Exception:
            pass

    # Clear cookies
    response = make_response(jsonify({"message": "Logged out successfully"}))
    unset_jwt_cookies(response)
    response.delete_cookie("csrf_access_token", path="/")
    response.delete_cookie("csrf_refresh_token", path="/")
    
    # Optional: block frontend from auto-refresh immediately
    response.set_cookie("refresh_token_cookie", "", expires=0, path="/")
    response.set_cookie("access_token_cookie", "", expires=0, path="/")
    
    return response, 200


# ---------- ADMIN USER MANAGEMENT ----------
@bp.route('/users', methods=['GET'])
@jwt_required()
def list_all_users():
    if not is_admin_request():
        return error_response("Admins only", 403)
    users = list_all_users_service()
    csrf_token = get_csrf_token(get_jwt())
    response = jsonify(users)
    response.set_cookie("csrf_access_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    response.set_cookie("csrf_refresh_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    return response, 200

@bp.route('/managers', methods=['GET'])
@jwt_required()
def list_all_managers():
    if not is_admin_request():
        return error_response("Admins only", 403)
    managers = list_all_managers_service()
    csrf_token = get_csrf_token(get_jwt())
    response = jsonify(managers)
    response.set_cookie("csrf_access_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    response.set_cookie("csrf_refresh_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    return response, 200

@bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_by_id(user_id):
    if not is_admin_request():
        return error_response("Admins only", 403)
    user = get_user_by_id_service(user_id)
    if not user:
        return error_response("User not found", 404)
    csrf_token = get_csrf_token(get_jwt())
    response = jsonify(user)
    response.set_cookie("csrf_access_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    response.set_cookie("csrf_refresh_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    return response, 200

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    if not is_admin_request():
        return error_response("Admins only", 403)
    success = delete_user_service(user_id)
    if not success:
        return error_response("User not found", 404)
    csrf_token = get_csrf_token(get_jwt())
    response = jsonify({"message": "User deleted"})
    response.set_cookie("csrf_access_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    response.set_cookie("csrf_refresh_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")
    return response, 200

@bp.route('/count', methods=['GET'])
def user_count():
    return jsonify({"count": count_users_service()}), 200

# ---------- PASSWORD RESET ----------
@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    if not email or not email.endswith(COMPANY_EMAIL_DOMAIN):
        return error_response("Invalid email domain", 400)
    message = forgot_password_service(email)
    return jsonify({"message": message}), 200

@bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')
    if not all([email, otp, new_password]):
        return error_response("Email, OTP, and new password are required", 400)
    if not email.endswith(COMPANY_EMAIL_DOMAIN):
        return error_response("Invalid email domain", 400)
    result = reset_password_service(email, otp, new_password)
    if result == "same_password":
        return error_response("New password must be different from the old password", 400)
    elif result is False:
        return error_response("Invalid OTP or failed to reset password", 400)
    return jsonify({"message": "Password reset successfully"}), 200
