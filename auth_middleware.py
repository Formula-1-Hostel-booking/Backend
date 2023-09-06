from functools import wraps
import jwt
from flask import request
from flask import current_app
from hostelHub.models.user_models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        response = {
            "data": {},
            "error_message": ""
        }

        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            response["error_message"] = "Token not provided"
            return response, 401
        try:
            data=jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user= User.query.filter_by(username=data["user"]).first()
            if current_user is None:
                response["error_message"] = "Invalid Authentication token!"
                return response, 401
           
        except Exception as e:
            response["error_message"] = str(e)
            return response ,500

        return f(*args, **kwargs)

    return decorated