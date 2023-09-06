import datetime
from flask import request

from hostelHub import app, db
from hostelHub.models.booking_models import (
    Booking, booking_schema,
)
from hostelHub.models.hostel_models import HostelRoomOccupant, HostelRoomType, hostel_room_occupant_schema, hostel_room_type_schema
from hostelHub.models.user_models import StudentProfile, studentprofile_schema
from hostelHub.routes.auth_middleware import token_required


# creating a new booking in the database
@token_required
@app.route('/booking', methods=['POST'])
def create_booking():
    # response structure
    response = {
        "data": {},
        "error_message": ""
    }

    # get details from frontend
    reference_number = request.json['reference_number']
    room_type_id = request.json['room_type_id']
    room_type_id = int(room_type_id)

    # check if student with given reference number exists
    student = StudentProfile.query.filter_by(
        reference_number=reference_number).first()
    if not student:
        response['error_message'] = f"Student with reference number {reference_number} does not exist"
        return response, 400

    # check if the student already has a room
    already_a_tenant = HostelRoomOccupant.query.filter_by(
        student=student.reference_number).first()
    if already_a_tenant:
        response['error_message'] = 'You already have a room'
        return response, 400

    # check to see if the user has already booked a room
    already_booked = Booking.query.filter_by(
        student=student.reference_number).first()
    if already_booked:
        response['error_message'] = 'You have already booked. Kindly go and make payment'
        return response, 400

    # checking to see if that room exists
    room = HostelRoomType.query.filter_by(id=room_type_id).first()

    if room:
        # check if the particular room is empty
        if student.gender == 'male' and room.available_male_bed_spaces == 0:
            response["error_message"] = "Male bed space unavailable"
            return response, 400

        if student.gender == 'female' and room.available_female_bed_spaces == 0:
            response["error_message"] = "Female bed space unavailable"
            return response, 400

        # making the booking
        booking = Booking(student=student.reference_number,
                          hostelroomtype_id=room.id)
        db.session.add(booking)
        db.session.commit()

        # serializing the response
        student_profile = studentprofile_schema.dump(student)

        # response
        response["data"]["student_profile"] = student_profile
        response["data"]["booking_id"] = booking.booking_id
        return response, 200

    else:
        response["error_message"] = 'No such room exists'
        return response, 400


# updating a particular booking
# when a payment is made, this routes confirms the booking and assigns a room to the user
@token_required
@app.route('/bookings/update', methods=['PUT', 'POST'])
def update_booking():
    response = {
        "data": {},
        "error_message": ""
    }

    # data required from the frontend
    booking_details = request.json['booking_details']
    user_details = request.json['user_details']
    room_details = request.json['room_details']
    hostel_details = request.json['hostel_details']

    # check if the student already has a room
    already_a_tenant = HostelRoomOccupant.query.filter_by(
        student=user_details['username']).first()
    if already_a_tenant:
        response['error_message'] = 'You already have a room'
        return response, 400

    # check to see if the user has already booked a room
    already_booked = Booking.query.filter_by(
        student=user_details['username']).first()
    if not already_booked:
        response['error_message'] = 'You have not booked. kindly go and book'
        return response, 400

    # we check if there are still available rooms
    room = HostelRoomType.query.filter_by(id=room_details['id']).first()
    if user_details['gender'] == 'male' and room.available_male_bed_spaces == 0:
        response['error_message'] = 'No male bed space available'
        return response, 400
    if user_details['gender'] == 'female' and room.available_female_bed_spaces == 0:
        response['error_message'] = 'No female bed space available'
        return response, 400

    # check if payment has actually been made
    if booking_details["payment_made"] == False:
        response["error_message"] = "Payment has not been made"
        return response, 400

    # this is to check if the person has already made the booking
    booking = Booking.query.filter_by(
        booking_id=booking_details['booking_id']).first()
    if booking:
        # time difference between date of booking and payment date
        payment_datetime = datetime.datetime.now()
        time_diff = booking.booking_datetime - payment_datetime

        # if time exceeds 3 days, delete the booking from the database
        if time_diff.days > 3:
            db.session.delete(booking)
            db.session.commit()
            response["error_message"] = "Please rebook"
            return response, 400

        # allocate a room to the individual
        roomoccupant = HostelRoomOccupant(student=user_details['username'])
        db.session.add(roomoccupant)
        db.session.commit()

        # reducing the number of bed spaces
        if user_details['gender'] == 'male':
            room.available_male_bed_spaces -= 1
        if user_details['gender'] == 'female':
            room.available_female_bed_spaces -= 1

        # get the hostel name
        hostel_name = hostel_details['hostel_name']
        split_hostel_name = [*hostel_name]
        room_number = ''
        for i in range(3):
            room_number += split_hostel_name[i]

        room_number += str(room.type)+'-'
        if user_details['gender'] == 'male':
            room_number_integer = (
                (room.male_bed_spaces-room.available_male_bed_spaces)//room.type)+1
            room_number += str(room_number_integer)+'-male'
        if user_details['gender'] == 'female':
            room_number_integer = (
                (room.female_bed_spaces-room.available_female_bed_spaces)//room.type)+1
            room_number += str(room_number_integer)+'-female'

        roomoccupant = hostel_room_occupant_schema.dump(roomoccupant)

        # updating the booking
        # booking.hostelroomtype_id = roomoccupant.id
        booking.payment_made = True
        booking.payment_id = ""
        booking.payment_datetime = payment_datetime
        db.session.commit()
        booking = booking_schema.dump(booking)

        db.session.add(room)
        db.session.commit()
        room = hostel_room_type_schema.dump(room)

        response["data"]["booking_details"] = booking
        response['data']['room_occupant'] = roomoccupant
        response['data']['room_details'] = room
        response['data']['room_number'] = room_number

        return response, 200
    else:
        response['error_message'] = 'No booking has been made. Please make booking before payment'
        return response, 400