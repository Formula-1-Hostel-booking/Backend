# this file contains all our models for  the databases

from hostelHub import db, ma, admin
import datetime
from .utils import CustomModelView
import random


def generate_random_string():
    random_id = (random.randint(100000, 999999))

    check = Booking.query.filter_by(booking_id=random_id)

    if check:
        return random.randint(100000, 999999)
    else:
        return random_id


class Booking(db.Model):
    __tablename__ = 'booking'
    booking_id = db.Column(db.Integer, primary_key=True,
                           default=generate_random_string)
    student = db.Column(db.String(20), db.ForeignKey(
        'studentprofile.reference_number'))
    booking_datetime = db.Column(db.DateTime(), default=datetime.datetime.now)
    hostelroomtype_id = db.Column(
        db.Integer, db.ForeignKey('hostelroomtype.id'))
    payment_made = db.Column(db.Boolean(), default=False)
    payment_id = db.Column(db.String(30))
    payment_datetime = db.Column(db.DateTime())

    def __repr__(self):
        return str(self.booking_id)


class BookingSchema(ma.Schema):
    class Meta:
        fields = ('booking_id', 'payment_made', 'payment_id',
                  'payment_datetime', 'student')


booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)


# ADMIN
class BookingModelView(CustomModelView):
    column_list = ['booking_id', 'payment_made',
                   'payment_id', 'payment_datetime', 'student']


admin.add_view(BookingModelView(Booking, db.session))
