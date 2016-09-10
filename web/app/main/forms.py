from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Email, Length, Required
from  ..models import User
from flask_wtf import Form
from wtforms import ValidationError


class SignupForm(Form):
    submit = SubmitField('Anmäl mig')

class ProfileForm(Form):
    email = StringField('Email', validators=[Required(),
                                             Length(0, 254),
                                             Email()])
    first_name = StringField('Förnamn', validators=[Length(0, 64)])
    last_name = StringField('Efternamn', validators=[Length(0, 64)])
    phone = StringField('Telefonnummer', validators=[Length(0, 32)])

    submit = SubmitField('Spara')
