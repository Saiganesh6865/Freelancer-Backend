# app/utils/response.py
def success_response(message, data=None, code=200):
    response = {"success": True, "message": message}
    if data is not None:
        response["data"] = data
    return response, code

def error_response(message, code=400):
    return {"success": False, "error": message}, code
