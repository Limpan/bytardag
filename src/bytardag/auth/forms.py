from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import Email, Length, DataRequired
from flask_wtf import FlaskForm


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(0, 254), Email()])
    password = PasswordField("Lösenord", validators=[DataRequired(), Length(6, 128)])
    submit = SubmitField("Registrera")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(0, 254), Email()])
    password = PasswordField("Lösenord", validators=[DataRequired(), Length(6, 128)])
    remember_me = BooleanField("Kom ihåg mig")
    submit = SubmitField("Registrera")
