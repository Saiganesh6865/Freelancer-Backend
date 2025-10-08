from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import (
    jwt_required, set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies, verify_jwt_in_request, get_jwt
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
from app.repositories.user_repository import is_admin_request
from app.utils.response import error_response
import uuid


bp = Blueprint('user', __name__, url_prefix='/user')
COMPANY_EMAIL_DOMAIN = "@company.com"


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return error_response("Missing JSON body", 422)

    result = authenticate_and_generate_tokens(data)
    if "error" in result:
        return error_response(result["error"], result.get("code", 401))

    response_data = {"user": result["user"], "success": True}
    response = make_response(jsonify(response_data))
    set_access_cookies(response, result["access_token"])
    set_refresh_cookies(response, result["refresh_token"])
    return response, 200


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    result = refresh_tokens()
    if "error" in result:
        return error_response(result["error"], result.get("code", 401))

    response = make_response(jsonify(result["user"]))
    set_access_cookies(response, result["access_token"])
    set_refresh_cookies(response, result["refresh_token"])
    return response, 200


# New endpoint: create first admin if none exists
@bp.route('/create-admin', methods=['POST'])
def create_admin():
    total_users = count_users_service()
    
    if total_users > 0:
        return error_response(
            "Admin already exists. Use regular signup with admin authorization.",
            403
        )

    data = request.get_json()
    if not data:
        return error_response("Missing JSON body", 422)

    # Force role to admin
    data["role"] = "admin"

    result = signup_user(total_users, data)

    if "error" in result:
        return error_response(result["error"], result.get("code", 400))

    return jsonify({"success": True, "message": "Admin created successfully", "user": result.get("user")}), 201


# Existing signup remains the same for normal users
@bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data:
        return error_response("Missing JSON body", 422)

    total_users = count_users_service()

    # Normal signup: only after first admin exists
    if total_users == 0:
        return error_response("Admin not created yet. Use /create-admin first.", 403)

    try:
        verify_jwt_in_request()
    except Exception:
        return error_response("Admin authorization required", 401)

    if not is_admin_request():
        return error_response("Only admin can create new users", 403)

    result = signup_user(total_users, data)

    if "error" in result:
        return error_response(result["error"], result.get("code", 400))

    return jsonify(result), result.get("status", 200)

@bp.route('/session', methods=['GET'])
def check_session():
    result = check_session_service(request)
    if "error" in result:
        return jsonify({"error": result["error"]}), result.get("code", 401)

    response = jsonify({"user": result["user"]})
    if "new_access_token" in result:
        set_access_cookies(response, result["new_access_token"])
    return response, 200

# @bp.route('/csrf-token', methods=['GET'])
# def get_csrf_token():
#     token = str(uuid.uuid4())  # generate a random token
#     response = jsonify({"csrf_token": token})
#     # Store token in secure cookie (optional)
#     response.set_cookie("csrf_access_token", token, httponly=True, secure=True, samesite='Strict')
#     return response, 200

    
 # ---------- CSRF Token Route (optional but helpful) ----------

@bp.route("/csrf-token", methods=["GET"])
def csrf_token():
    """
    Returns the current CSRF token (if logged in) for frontend to use.
    No new token is created; it just reads the one from JWT cookies.
    """
    verify_jwt_in_request_optional()  # doesn't raise if token missing
    token = get_csrf_token(request.cookies.get("access_token_cookie"))
    if not token:
        return jsonify({"error": "No active CSRF token"}), 401
    return jsonify({"csrf_token": token}), 200


# @bp.route('/logout', methods=['POST'])
# @jwt_required()
# def logout():
#     jwt_data = get_jwt()   # get the decoded JWT payload
#     result = logout_user(jwt_data)

#     response = make_response(jsonify({"message": result["message"]}))
#     unset_jwt_cookies(response)
#     return response, result.get("code", 200)

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jwt_data = get_jwt()  # get the decoded JWT payload
    result = logout_user(jwt_data)

    response = make_response(jsonify({"message": result["message"]}))

    # Remove JWT cookies
    unset_jwt_cookies(response)

    # Also remove CSRF cookies
    response.delete_cookie("csrf_access_token", path="/")
    response.delete_cookie("csrf_refresh_token", path="/")

    return response, result.get("code", 200)


@bp.route('/users', methods=['GET'])
@jwt_required()
def list_all_users():
    if not is_admin_request():
        return error_response("Admins only", 403)

    users = list_all_users_service()
    return jsonify(users), 200


@bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_by_id(user_id):
    if not is_admin_request():
        return error_response("Admins only", 403)

    user = get_user_by_id_service(user_id)
    if not user:
        return error_response("User not found", 404)
    return jsonify(user), 200


@bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    if not is_admin_request():
        return error_response("Admins only", 403)

    success = delete_user_service(user_id)
    if not success:
        return error_response("User not found", 404)
    return jsonify({"message": "User deleted"}), 200


@bp.route('/count', methods=['GET'])
def user_count():
    return jsonify({"count": count_users_service()}), 200


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









