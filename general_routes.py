import os 
from flask import request, send_from_directory
from hostelHub import app 
from hostelHub.routes.auth_middleware import token_required

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path,
                                   'favicon.ico',mimetype='image/vnd.microsoft.icon')

@token_required
@app.route('/payment/verify')
def verify_payment():
    response = {
        "data": {},
        "error_message": ""
    }

    # get data from request body
    payment_reference = request.json.get("payment_reference")
    
    # validate data
    if not payment_reference:
        response["error_message"] = "Payment reference not provided"
        return response, 400

    