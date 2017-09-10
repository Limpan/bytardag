from wtforms import BooleanField, DateTimeField, IntegerField, StringField, SubmitField, PasswordField
from wtforms.validators import Email, Length, Required
from  ..models import User
from flask_wtf import FlaskForm
from wtforms import ValidationError


class SignupForm(FlaskForm):
    submit = SubmitField('Anmäl mig')


class ProfileForm(FlaskForm):
    email = StringField('Email', validators=[Required(),
                                             Length(0, 254),
                                             Email()])
    first_name = StringField('Förnamn', validators=[Length(0, 64)])
    last_name = StringField('Efternamn', validators=[Length(0, 64)])
    phone = StringField('Telefonnummer', validators=[Length(0, 32)])
    submit = SubmitField('Spara')


class BankAccountForm(FlaskForm):
    bank = StringField('Bank', validators=[Required(), Length(0, 64)])
    clearing = StringField('Clearingnummer', validators=[Length(0, 16)])
    number = StringField('Kontonummer', validators=[Length(0, 64)])
    submit = SubmitField('Spara')


class VolunteerForm(FlaskForm):
    available_week_before = BooleanField('En vecka innan')
    available_thursday = BooleanField('Torsdag')
    available_friday = BooleanField('Fredag')
    available_saturday_part_a = BooleanField('Lördag förmiddag')
    available_saturday_part_b = BooleanField('Lördag eftermiddag')
    available_sunday = BooleanField('Söndag')
    submit = SubmitField('Anmäl')


class EventForm(FlaskForm):
    start = DateTimeField('Start')
    end = DateTimeField('Slut')
    signup_start = DateTimeField('Anmälan öppnar')
    signup_end = DateTimeField('Anmälan stänger')
    limit = IntegerField('Max antal deltagare')
    submit = SubmitField('Skapa nytt')
