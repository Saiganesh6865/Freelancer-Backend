# app/utils/response.py
def success_response(data):
    return {"success": True, "data": data}, 200

def error_response(message, code=400):
    return {"success": False, "error": message}, code