# this file contains all our models for  the databases
from hostelHub import db, ma, admin, app
from hostelHub import login_manager
from hostelHub.models.utils import CustomModelView

from sqlalchemy import event

from flask_admin.form import fields

from flask import url_for
from flask_security import (
    Security, SQLAlchemyUserDatastore,
    UserMixin, RoleMixin, LoginForm, RegisterForm,
    )
from flask_security.utils import hash_password
from flask_admin import helpers as admin_helpers
from wtforms import StringField, validators

# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.String(50), db.ForeignKey('user.username')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(60), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    student = db.relationship('StudentProfile', backref='user_account', lazy=True, uselist=False)
    hostel_manager = db.relationship('HostelManagerProfile', backref='user_account', lazy=True, uselist=False)

    def __repr__(self):
        return f'{self.username}'

# ensure user has only one role
@event.listens_for(User, 'before_insert')
@event.listens_for(User, 'before_update')
def ensure_one_role_per_user(mapper, connection, target):
    if len(target.roles) > 1:
        raise ValueError("User should have only one role")

class ExtendedRegisterForm(RegisterForm):
        username = StringField(
            "Username",
            validators=[
                validators.data_required(),
            ]
        )

        def validate(self, extra_validators=None):
            if User.query.filter_by(username=self.username.data).first():
                self.username.errors = list(self.username.errors)
                self.username.errors.append("Username already exists")
                return False
            return super().validate(extra_validators)

class ExtendedLoginForm(LoginForm):
        def validate(self):
            user=User.query.filter_by(email=self.email.data).first()

            if user and "admin" not in user.roles:
                self.email.errors = list(self.email.errors)
                self.email.errors.append("You do not have authorization for this site")
                return False
            return super().validate()




# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(
    app=app,
    datastore=user_datastore,
    register_form=ExtendedRegisterForm,
    login_form=ExtendedLoginForm,
)

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for,
    )

class UserSchema(ma.Schema):
    class Meta:
        fields = ('username', 'email')

# initializing schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)
        



class StudentProfile(db.Model):
    __tablename__ = 'studentprofile'
    reference_number = db.Column(db.String(8), primary_key=True)
    user = db.Column(db.String(50), db.ForeignKey('user.username'), nullable=False)
    first_name = db.Column(db.String(20), nullable = False)
    last_name = db.Column(db.String(20), nullable = False)
    other_names = db.Column(db.String(20))
    phone_number = db.Column(db.String(20), nullable = False)
    program_of_study = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    hostel_room_occupant = db.relationship('HostelRoomOccupant', backref='roomoccupant',lazy=True, uselist=False)
    
    def __repr__(self):
     return f'{self.reference_number}'

    booking = db.relationship('Booking', backref='booking', lazy=True)


class StudentProfileSchema(ma.Schema):
    class Meta:
        fields = ('reference_number', 'email','password','first_name','last_name','other_names','phone_number','program_of_study','gender')

studentprofile_schema = StudentProfileSchema()
studentprofiles_schema = StudentProfileSchema(many = True)
        

class HostelManagerProfile(db.Model):
    __tablename__ = 'hostelmanagerprofile'
    manager_id = db.Column(db.String(6), primary_key=True)
    user = db.Column(db.String(50), db.ForeignKey('user.username'), nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    other_names = db.Column(db.String(20))
    phone_number = db.Column(db.String(20), nullable=False)

    hostel = db.relationship('Hostel', backref='hostelmanagerprofile', lazy=True, uselist=False)

    def __repr__(self):
     return f'{self.manager_id} - {self.first_name} {self.last_name}'



class HostelManagerProfileSchema(ma.Schema):
    class Meta:
        fields = ('manager_id', 'username', 'first_name', 'last_name', 'other_names', 'phone_number')

hostel_manager_profile_schema = HostelManagerProfileSchema()
hostel_manager_profiles_schema = HostelManagerProfileSchema(many=True)



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Admin Model Views ~~~~~~~~~~~~~~~~~~~~~ 


class UserModelView(CustomModelView):
    form_columns = ['username', 'email', 'password', 'roles']
    column_list = ['username', 'email', 'roles']
    
    # use this to edit HTML attributes of the form inputs
    form_widget_args = {
        'password':{
            'type': "password"
        },
        'email': {
            'placeholder': 'enter email'
        }
    }

    def on_model_change(self, form, model, is_created):
        # If creating a new user, hash password
        if is_created:
            model.password = hash_password(form.password.data)
        else:
            old_password = form.password.object_data
            # If password has been changed, hash password
            if not old_password == model.password:
                model.password = hash_password(form.password.data)

    def validate_form(self, form):
        # ensure only one role is selected
        if hasattr(form, 'roles') and len(form.roles.data) > 1:
            form.roles.errors = list(form.roles.errors)
            form.roles.errors.append("User should have only one role")
            return False

        return super().validate_form(form)

admin.add_view(UserModelView(User, db.session))

class StudentProfileView(CustomModelView):
    form_columns = [
        'user_account',
        'first_name', 'last_name', 'other_names',
        'reference_number', 'phone_number', 'program_of_study',
        'gender'
        ]
    
    form_overrides = {
        'gender': fields.Select2Field
    }

    form_args = {
        'gender': {
            'choices': [
                ('male', 'male'),
                ('female', 'female'),
            ]
        }
    }

admin.add_view(StudentProfileView(StudentProfile, db.session))


class HostelManagerProfileView(CustomModelView):
    form_columns = [
        'manager_id', 'user_account', 
        'first_name', 'last_name', 'other_names',
        'phone_number', 'hostel'
    ]
    column_list = [
        'manager_id', 'user_account', 
        'first_name', 'last_name', 'other_names',
        'phone_number', 'hostel'
    ]



admin.add_view(HostelManagerProfileView(HostelManagerProfile, db.session))

# ~~~~~~~~~~~~~~~~~~~~~~ GENERIC ~~~~~~~~~~~~~~~~~~
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# @app.before_first_request
# def before_first_request():
#     # create all tables
#     db.create_all()
#     student_role = Role(name="student")
#     manager_role = Role(name="manager ")
#     admin_role = Role(name="admin")
#     db.session.add_all([student_role, manager_role, admin_role])
#     db.session.commit()