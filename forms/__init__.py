from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    # Personal Details
    first_name = StringField('First Name (as in National ID)', validators=[DataRequired(), Length(max=50)])
    surname = StringField('Surname (as in National ID)', validators=[DataRequired(), Length(max=50)])
    other_names = StringField('Other Names', validators=[Length(max=100)])
    date_of_birth = StringField('Date of Birth', validators=[DataRequired()])
    national_id = StringField('National ID/Passport Number', validators=[DataRequired(), Length(max=50)])
    
    # Contact Information
    phone_number = StringField('Phone Number (mobile)', validators=[DataRequired(), Length(max=15)])
    alt_phone_number = StringField('Alternative Phone Number', validators=[Length(max=15)])
    email = StringField('Email Address', validators=[Email()])
    
    # Address
    physical_address = StringField('Physical Address', validators=[DataRequired(), Length(max=200)])
    district = SelectField('District', choices=[
        ('Lilongwe', 'Lilongwe'),
        ('Blantyre', 'Blantyre'),
        ('Mzuzu', 'Mzuzu'),
        ('Zomba', 'Zomba'),
        ('Kasungu', 'Kasungu'),
        ('Mangochi', 'Mangochi'),
        ('Salima', 'Salima'),
        ('Nkhata Bay', 'Nkhata Bay')
    ], validators=[DataRequired()])
    city_town = StringField('City/Town/Village', validators=[DataRequired(), Length(max=100)])
    
    # Fishing Details
    license_type = SelectField('Type of License', choices=[
        ('freshwater', 'Freshwater'),
        ('saltwater', 'Saltwater'),
        ('recreational', 'Recreational'),
        ('commercial', 'Commercial')
    ], validators=[DataRequired()])
    fishing_method = SelectField('Fishing Method', choices=[
        ('rod_line', 'Rod/Line'),
        ('net', 'Net'),
        ('trap', 'Trap'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    fishing_location = SelectField('Fishing Location', choices=[
        ('lake_malawi', 'Lake Malawi'),
        ('lake_chilwa', 'Lake Chilwa'),
        ('shire_river', 'Shire River'),
        ('lake_malombe', 'Lake Malombe'),
        ('lake_chiuta', 'Lake Chiuta')
    ], validators=[DataRequired()])
    
    # Additional Information
    hear_about = SelectField('How did you hear about this license?', choices=[
        ('online', 'Online/Social Media'),
        ('newspaper', 'Newspaper'),
        ('radio', 'Radio'),
        ('tv', 'Television'),
        ('friend', 'Friend/Family'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    
    # Account Security
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    submit = SubmitField('Register')

    def validate_email(self, email):
        if email.data:  # Only validate if email is provided
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered. Please use another one.')

    def validate_national_id(self, national_id):
        user = User.query.filter_by(national_id=national_id.data).first()
        if user:
            raise ValidationError('This National ID/Passport Number is already registered.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class LicenseApplicationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    id_number = StringField('ID Number', validators=[DataRequired(), Length(max=50)])
    fishing_zone = SelectField('Fishing Zone', 
                             choices=[
                                 ('coastal', 'Coastal Waters'),
                                 ('inland', 'Inland Waters'),
                                 ('deep_sea', 'Deep Sea'),
                                 ('recreational', 'Recreational Fishing')
                             ],
                             validators=[DataRequired()])
    duration = SelectField('License Duration (months)',
                         choices=[(3, '3 Months'), (6, '6 Months'), (12, '12 Months')],
                         coerce=int,
                         validators=[DataRequired()])
    submit = SubmitField('Submit Application')