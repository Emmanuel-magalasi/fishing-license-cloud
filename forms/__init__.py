from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose another one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use another one.')

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