from flask import jsonify

def success_response(message, data=None, code=200):
    response = {
        "success": True,
        "message": message,
    }
    if data is not None:
        response["data"] = data
    return jsonify(response), code


def error_response(message, code=400):
    response = {
        "success": False,
        "message": message
    }
    return jsonify(response), code
