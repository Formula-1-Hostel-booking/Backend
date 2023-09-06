# this file handles all our routes
from flask import request
import datetime
import jwt
from hostelHub import app, db
from hostelHub.models.user_models import (
    User,
    StudentProfile, studentprofile_schema
    )
from hostelHub.models.hostel_models import (
    Hostel, hostels_schema
)

from flask_security.utils import verify_password, hash_password



@app.route('/login/student', methods=['POST'])
def login():
    response = {
        "data": {},
        "error_message": ""
    }

    # get data from request body
    username = request.json.get('username')
    password = request.json.get('password')
    
    # validate data
    if not username:
        response["error_message"] = "Username not provided"
        return response, 400
    if not password:
        response["error_message"] = "Password not provided"
        return response, 400
    
    # authenticate credentials
    user = User.query.filter_by(username=username).first()
    
    if user and verify_password(password, user.password):
        token = jwt.encode({'user':user.username,'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        # check the role of the user logging in
        if "student" not in user.roles:
            response["error_message"] = "These credentials don't belong to a student account"
            return response, 400 
        
        student_profile = StudentProfile.query.filter_by(user=user.username).first()
        student_profile = studentprofile_schema.dump(student_profile)
        
        # list of hostels
        hostels = Hostel.query.all()
        hostels = hostels_schema.dump(hostels)

        for hostel in hostels:
            # remove unwanted fields
            hostel.pop("manager_id")
            hostel.pop("ratings")

        response["data"]["student_profile"] = student_profile
        response["data"]["hostels"] = hostels
        response["data"]["auth-token"] = token
        return response, 200

    else:
        response["error_message"] = "Invalid Credentials/No such user"
        return response, 404

@app.route('/user/password/change', methods=['POST'])
def change_password():
    response = {
        "data": {},
        "error_message": ""
    }

    # get data from request body
    username = request.json.get('username')
    new_password = request.json.get('new_password')
    
    # validate data
    if not username:
        response["error_message"] = "Username not provided"
        return response, 400
    if not new_password:
        response["error_message"] = "New password not provided"
        return response, 400

    user = User.query.filter_by(username=username).first()
    if not user:
        response["error_message"] = f"User with username: {username} does not exist"
        return response, 404

    # set new password on user
    user.password = hash_password(new_password)
    db.session.add(user)
    db.session.commit()

    return response, 200    