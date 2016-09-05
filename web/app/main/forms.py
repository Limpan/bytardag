from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Email, Length, Required
from  ..models import User
from flask_wtf import Form
from wtforms import ValidationError


class RegisterForm(Form):
    email = StringField('Email', validators=[Required(),
                                             Length(0, 254),
                                             Email()])
    password = PasswordField('Lösenord', validators=[Required(),
                                                     Length(6, 128)])
    submit = SubmitField('Registrera')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email-adressen är redan registrerad.')


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
