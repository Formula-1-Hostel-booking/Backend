# this file contains all our models for  the databases
import uuid

from flask import url_for
from hostelHub import app, db, ma, admin
from hostelHub.models.utils import CustomModelView
 
from flask_admin.form.fields import Select2Field
from werkzeug.utils import secure_filename

from flask_admin_s3_upload import S3ImageUploadField, url_for_s3
from marshmallow import post_dump

class Hostel(db.Model):
    __tablename__ = 'hostel'
    hostel_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    location = db.Column(db.String(30), nullable = False)
    image= db.Column(db.String(200), nullable = False)
    ratings = db.Column(db.Integer,default=1)
    manager_id = db.Column(db.String(6), db.ForeignKey('hostelmanagerprofile.manager_id'), nullable = True)
    
    rooms = db.relationship('HostelRoomType', backref='hostel', lazy=True)
    facilities = db.relationship('HostelFacility', backref='hostel', lazy=True)
    

    def __str__(self):
        return self.name

class HostelSchema(ma.Schema):
    class Meta:
        fields = ('hostel_id', 'name','location', 'image', 'manager_id', 'ratings')
    
    @post_dump
    def get_full_image_url(self, data, **kwargs):
        # generate full URL of hostel images
        if not data["image"]:
            return data

        if app.config["S3_FILE_STORAGE_BACKEND"] == "s3":
            data["image"] =  url_for_s3('static', bucket_name=app.config["S3_BUCKET_NAME"], scheme="https", filename=data["image"])
        else:
            data["image"] = url_for('static', filename=data["image"], _external=True)
        return data

hostel_schema = HostelSchema()
hostels_schema = HostelSchema(many=True)



class HostelFacility(db.Model):
    __tablename__ = 'hostelfacility'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    image = db.Column(db.String(200), nullable=True) # to hold the image's url/path
    hostel_id = db.Column(db.Integer, db.ForeignKey('hostel.hostel_id'))

    def __str__(self):
        return f'{self.name} - {self.hostel.name}'

class HostelFacilitySchema(ma.Schema):
    class Meta:
        fields = ('id','name', 'image' )

    @post_dump
    def get_full_image_url(self, data, **kwargs):
        # generate full URL of hostel images
        if not data["image"]:
            return data

        if app.config["S3_FILE_STORAGE_BACKEND"] == "s3":
            data["image"] =  url_for_s3('static', bucket_name=app.config["S3_BUCKET_NAME"], scheme="https", filename=data["image"])
        else:
            data["image"] = url_for('static', filename=data["image"], _external=True)
        return data

hostelfacility_schema = HostelFacilitySchema()
hostelfacilities_schema = HostelFacilitySchema(many=True)




class HostelRoomType(db.Model):
    __tablename__= 'hostelroomtype'
    id = db.Column(db.Integer,primary_key=True)
    hostel_id = db.Column(db.Integer, db.ForeignKey('hostel.hostel_id'))
    type = db.Column(db.Integer,nullable=False, default=4)
    male_bed_spaces= db.Column(db.Integer, nullable=True, default = 0)
    available_male_bed_spaces = db.Column(db.Integer, nullable=True,  default=0)
    female_bed_spaces = db.Column(db.Integer, nullable=True,  default=0)
    available_female_bed_spaces= db.Column(db.Integer, nullable=True, default=0)
    price = db.Column(db.Float,default=0)

        


class HostelRoomTypeSchema(ma.Schema):
    class Meta:
        fields = ('id', 'type', 'available_male_bed_spaces', 'available_female_bed_spaces', 'price')

hostel_room_type_schema = HostelRoomTypeSchema()
hostel_rooms_type_schema = HostelRoomTypeSchema(many=True)


class HostelRoomOccupant(db.Model):
    __tablename__ = 'hostelroomoccupant'
    id = db.Column(db.Integer, primary_key=True)
    student = db.Column(db.String(8), db.ForeignKey('studentprofile.reference_number'))
    room_number = db.Column(db.String(20))
    # hostel_id = db.Column(db.Integer, db.ForeignKey('hostel.hostel_id'))
    

class HostelRoomOccupantSchema(ma.Schema):
    class Meta:
        fields = ('id', 'student')

hostel_room_occupant_schema = HostelRoomOccupantSchema()
hostel_room_occupants_schema = HostelRoomOccupantSchema(many=True)


class HostelModelView(CustomModelView):
    form_columns = ['name', 'location', 'image', 'ratings']
    column_list = ['hostel_id', 'name', 'location', 'hostelmanagerprofile', 'ratings']

    form_overrides= {
        'image' : S3ImageUploadField,
        'ratings': Select2Field,
      
    }


    def prefix_name(obj, file_data):
        filename = secure_filename(file_data.filename)
        filename = str(uuid.uuid1()) + '-' + filename
        return filename
    
    form_args = {
        'image': {
            'base_path': app.config['UPLOAD_FOLDER'],
            'relative_path': 'hostels/',
            'allow_overwrite': True,
            'namegen': prefix_name,

            # flask_admin_s3_upload
            'storage_type': app.config['S3_FILE_STORAGE_BACKEND'],
            'bucket_name': app.config["S3_BUCKET_NAME"],
            "access_key_id": app.config["S3_ACCESS_KEY_ID"],
            "access_key_secret": app.config["S3_ACCESS_KEY_SECRET"],
            "static_root_parent": app.config["S3_STATIC_ROOT_PARENT"],
            "storage_type_field": 's3',
            "bucket_name_field": 'formula1-hostel-booking',

        },
         'ratings': {
            'choices': [
                ('1', '1'),
                ('2', '2'),
                ('3','3'),
                ('4','4'),
                ('5','5'),    
            ]
         },
         'type' :{
            'choices':[
                ('4','4'),
                ('3','3'),
                ('2','2'),
                ('1','1'),

            ]
            
    }
        
    }

    
    

class HostelFacilityModelView(CustomModelView):

    form_overrides = {
        'image' : S3ImageUploadField,
        'name': Select2Field,
        
    }


    def prefix_name(obj, file_data):
        filename = secure_filename(file_data.filename)
        filename = str(uuid.uuid1()) + '-' + filename
        return filename

    form_args = {
        'image': {
            'base_path': app.config['UPLOAD_FOLDER'],
            'relative_path': 'hostel_facilities/',
            'allow_overwrite': True,
            'namegen': prefix_name,

            # flask_admin_s3_upload
            'storage_type': app.config['S3_FILE_STORAGE_BACKEND'],
            'bucket_name': app.config["S3_BUCKET_NAME"],
            "access_key_id": app.config["S3_ACCESS_KEY_ID"],
            "access_key_secret": app.config["S3_ACCESS_KEY_SECRET"],
            "static_root_parent": app.config["S3_STATIC_ROOT_PARENT"],
            "storage_type_field": 's3',
            "bucket_name_field": 'formula1-hostel-booking',
        },
        'name': {
            'choices': [
                ('air_conditioner', 'Air Conditioner'),
                ('wi_fi', 'Wi-Fi'),
                ('canteen', 'Canteen'),
                ('parking_lot', 'Parking Lot'),
                ('study_room', 'Study Room'),
                ('basket_ball_court', 'Basket Ball Court'),
                ('volley_ball_court', 'Volley Ball Court'),
                ('tv_room', 'TV Room'),
                ('1_in_a_room', '1 In A Room'),
                ('2_in_a_room', '2 In A Room'),
                ('3_in_a_room', '3 In A Room'),
                ('4_in_a_room', '4 In A Room'),
            ]
        },
        
    }

class HostelRoomTypeModelView(CustomModelView):
    
    form_overrides = {
    'type':Select2Field
        
    }
    form_args = {
        'type':{
            'choices':[
                ('1','1'),
                ('2','2'),
                ('3','3'),
                ('4','4'),
            ]
        }
    }

    def validate_form(self, form):
        if (form.male_bed_spaces.data < form.available_male_bed_spaces.data ):
            form.available_male_bed_spaces.errors =list(form.available_male_bed_spaces.errors)
            form.available_male_bed_spaces.errors.append("Male bed spaces exceed available number")
            return False

        if(form.female_bed_spaces.data<form.available_female_bed_spaces.data):
           form.available_female_bed_spaces.errors =list(form.available_female_bed_spaces.errors) 
           form.available_female_bed_spaces.errors.append("Female bed spaces exceed available number")
           return False

        if (form.price.data<0):
            form.price.errors = list(form.price.errors)
            form.price.errors.append("Prices can not be less than 0")
            return False
    
        if (form.male_bed_spaces.data<0):
            form.male_bed_spaces.errors = list(form.male_bed_spaces.errors)
            form.male_bed_spaces.errors.append("Bedspaces cannot be negative")
            return False

        if (form.female_bed_spaces.data<0):
            form.female_bed_spaces.errors = list(form.female_bed_spaces.errors)
            form.female_bed_spaces.errors.append("Bedspaces cannot be negative")
            return False
        if (form.available_male_bed_spaces.data<0):
            form.available_male_bed_spaces.errors = list(form.available_male_bed_spaces.errors)
            form.available_male_bed_spaces.errors.append("Bedspaces cannot be negative")
            return False

        if (form.available_female_bed_spaces.data<0):
            form.available_female_bed_spaces.errors = list(form.available_female_bed_spaces.errors)
            form.available_female_bed_spaces.errors.append("Bedspaces cannot be negative")
            return False
        
        return super().validate_form(form)


admin.add_view(HostelModelView(Hostel, db.session))
admin.add_view(HostelFacilityModelView(HostelFacility, db.session))
admin.add_view(HostelRoomTypeModelView(HostelRoomType, db.session))
admin.add_view(CustomModelView(HostelRoomOccupant, db.session))

