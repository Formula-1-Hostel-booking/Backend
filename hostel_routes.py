from hostelHub import app
from hostelHub.models.user_models import HostelManagerProfile, hostel_manager_profile_schema

from hostelHub.routes.auth_middleware import token_required
from hostelHub.models.hostel_models import (
    Hostel, hostel_schema,
    HostelRoomType, hostel_room_type_schema,
    HostelFacility, hostelfacilities_schema
)


# viewing a particular hostel

@token_required
@app.route('/hostels/<int:hostel_id>', methods=['GET'])
def view_hostel(hostel_id):
    response = {
        "data": {},
        "error_message": ""
    }
    response_data = {
        "hostel_details": {},
        "hostel_manager": {},
        "hostel_facilities": [],
        "hostel_carousel_images": [],
        "hostel_room_types": []
    }

    # hostel details
    hostel = Hostel.query.get(hostel_id)
    if not hostel:
        response["error_message"] = f"Hostel with id {hostel_id} does not exist"
        return response, 404

    # clean data
    hostel = hostel_schema.dump(hostel)

    hostel_image = hostel.pop("image")
    hostel_manager_id = hostel.pop("manager_id")
    response_data["hostel_details"] = hostel

    # hostel manager details
    manager = HostelManagerProfile.query.get(hostel_manager_id)
    if manager:
        response_data["hostel_manager"] = hostel_manager_profile_schema.dump(
            manager)

    # hostel facilities and hostel carousel images
    hostel_facilities = HostelFacility.query.filter_by(hostel_id=hostel_id)
    hostel_facilities = hostelfacilities_schema.dump(
        hostel_facilities, many=True)

    # populate hostel carousel images
    for hostel_facility in hostel_facilities:
        if hostel_facility["image"]:
            response_data["hostel_carousel_images"].append(
                hostel_facility["image"])
    response_data["hostel_carousel_images"].append(hostel_image)

    # populate hostel facilities
    for hostel_facility in hostel_facilities:
        if not "room" in hostel_facility["name"]:
            response_data["hostel_facilities"].append(hostel_facility["name"])

    # populate hostel room types
    hostel_room_types = HostelRoomType.query.filter_by(hostel_id=hostel_id)
    hostel_room_types = hostel_room_type_schema.dump(
        hostel_room_types, many=True)
    print(hostel_room_types)
    response_data["hostel_room_types"] = sorted(hostel_room_types, key=lambda x: x["type"])

    response["data"] = response_data

    return response, 200
