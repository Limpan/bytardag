from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import Email, EqualTo, Length, Regexp, Required
from  ..models import User
from flask_wtf import FlaskForm
from wtforms import ValidationError


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(),
                                             Length(1, 254),
                                             Email()])
    password = PasswordField('Lösenord', validators=[Required()])
    remember_me = BooleanField('Håll mig inloggad')
    submit = SubmitField('Logga in')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[Required(),
                                             Length(0, 254),
                                             Email()])
    password = PasswordField('Lösenord', validators=[Required(),
                                                     Length(6, 128)])
    first_name = StringField('Förnamn', validators=[Required(),
                                                  Length(1, 64)])
    last_name = StringField('Efternamn', validators=[Required(),
                                                   Length(1, 64)])
    submit = SubmitField('Registrera')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email-adressen är redan registrerad.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Gammalt lösenord', validators=[Required()])
    password = PasswordField('Nytt lösenord', validators=[Required(),
                                                          EqualTo('password2',
                                                          message='Lösenorden måste matcha')])
    password2 = PasswordField('Verfiera nytt lösenord', validators=[Required()])
    submit = SubmitField('Byt lösenord')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[Required(),
                                             Length(1, 254),
                                             Email()])
    submit = SubmitField('Återställ lösenord')


class PasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[Required(),
                                             Length(1, 254),
                                             Email()])
    password = PasswordField('Nytt lösenord', validators=[Required(),
                                                          EqualTo('password2',
                                                          message='Lösenorden måste matcha')])
    password2 = PasswordField('Verfiera lösenord', validators=[Required()])
    submit = SubmitField('Återställ lösenord')

    def validate_email(self, field):
        """Used to check if the email adress already exists in the database."""
        if User.query.filter_by(email=field.data.lower()).first() is None:
            raise ValidationError('Okänd email-adress.')


class ChangeEmailForm(FlaskForm):
    email = StringField('Ny Email', validators=[Required(),
                                                Length(1, 64),
                                                Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Uppdatera Email-adress')

    def validate_email(self, field):
        """Used to check if the email adress already exists in the database.

        Raises an ValidationError if the email-adress is already registrated.
        """
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email-adressen är redan registrerad.')
