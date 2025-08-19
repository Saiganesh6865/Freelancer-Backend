from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import (
    jwt_required, get_jwt_identity,
    set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies, get_jwt, verify_jwt_in_request
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

bp = Blueprint('user', __name__, url_prefix='/user')


COMPANY_EMAIL_DOMAIN = "@company.com"

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return error_response("Missing JSON body", 422)

        result = authenticate_and_generate_tokens(data)
        if "error" in result:
            return error_response(result["error"], result.get("code", 401))

        response = make_response(jsonify(result["user"]))
        set_access_cookies(response, result["access_token"])
        set_refresh_cookies(response, result["refresh_token"])
        return response, 200

    except Exception as e:
        print("Login error:", e)
        return error_response("Internal server error", 500)


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        result = refresh_tokens()
        if "error" in result:
            return error_response(result["error"], result.get("code", 401))

        response = make_response(jsonify(result["user"]))
        set_access_cookies(response, result["access_token"])
        set_refresh_cookies(response, result["refresh_token"])
        return response, 200

    except Exception as e:
        print("Refresh error:", e)
        return error_response("Internal server error", 500)


@bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        if not data:
            return error_response("Missing JSON body", 422)

        total_users = count_users_service()
        # Delegate to service with count and data
        result = signup_user(total_users, data)
        if "error" in result:
            return error_response(result["error"], result.get("code", 400))

        return jsonify(result), result.get("status", 200)

    except Exception as e:
        print("Signup error:", e)
        return error_response("Internal server error", 500)


@bp.route('/session', methods=['GET'])
def check_session():
    try:
        result = check_session_service(request)
        if "error" in result:
            return jsonify({"error": result["error"]}), result.get("code", 401)

        response = jsonify({"user": result["user"]})
        if "new_access_token" in result:
            set_access_cookies(response, result["new_access_token"])
        return response, 200

    except Exception as e:
        print("Session check error:", e)
        return jsonify({"error": "Unauthorized"}), 401


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        result = logout_user(get_jwt())
        response = make_response(jsonify({"message": result["message"]}))
        unset_jwt_cookies(response)
        return response, result.get("code", 200)

    except Exception as e:
        print("Logout error:", e)
        return error_response("Internal server error", 500)


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
    total = count_users_service()
    return jsonify({"count": total}), 200



@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    if not email or not email.endswith(COMPANY_EMAIL_DOMAIN):
        return error_response("Invalid email domain", 400)

    try:
        # Call service function to generate/send OTP
        message = forgot_password_service(email)
        return jsonify({"message": message}), 200
    except Exception as e:
        print("Forgot password error:", e)
        return error_response("Internal server error", 500)


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

    try:
        # Call service function to verify OTP and reset password
        result = reset_password_service(email, otp, new_password)
        if result == "same_password":
            return error_response("New password must be different from the old password", 400)
        elif result is False:
            return error_response("Invalid OTP or failed to reset password", 400)

        return jsonify({"message": "Password reset successfully"}), 200
    except Exception as e:
        print("Reset password error:", e)
        return error_response("Internal server error", 500)