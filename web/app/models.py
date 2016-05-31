from flask import current_app, request, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
from sqlalchemy.dialects.postgresql import JSON
from app.exceptions import ValidationError
from datetime import datetime, time
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import hashlib

"""Add database model, see example in
https://github.com/miguelgrinberg/flasky/blob/master/app/models.py
"""


class Permission:
    SIGNUP_TO_EVENT = 0x01
    VOLUNTEER = 0x02
    READ_SHIFTS = 0x04
    MANAGE_SHIFTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    """Database model for the different roles."""
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        """Method for setting roles for user accounts if they are missing.

        Teacher-permissions is default.
        """
        roles = {
            'Seller': (Permission.SIGNUP_TO_EVENT, True),
            'Worker': (Permission.SIGNUP_TO_EVENT |
                       Permission.VOLUNTEER |
                       Permission.READ_SHIFTS, False),
            'Moderator': (Permission.SIGNUP_TO_EVENT |
                          Permission.VOLUNTEER |
                          Permission.READ_SHIFTS |
                          Permission.MANAGE_SHIFTS, False),
            'Administrator': (0xff, False)
        }

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class User(UserMixin, db.Model):
    """Database model for user accounts."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    password_hash = db.Column(db.String(128), default=None)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, **kwargs):
        """Init-method used for assigning roles.

        Gives the user with email BYTARDAG_ADMIN admin rights.
        """
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['BYTARDAG_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self, expiration=3600):
        """Used to generate a token for a password reset."""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        """Used to verify token and set new password."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        """Used to generate a token for an email change."""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        """Used to verify token and change email adress."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        db.session.commit()
        return True

    def can(self, permissions):
        """Used to check if a user has the given permissions."""
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        """Used to check if a user is administrator."""
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def generate_auth_token(self, expiration):
        """Return an auth token.

        Args:
            expiration:
                integer (seconds) before token expires
        """
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User {}>'.format(self.email)


# Loads a user for given user_id.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class AnonymousUser(AnonymousUserMixin):
    """Class for anonymous user, which returns false for permission checks."""
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


# Sets login_managers anonymous_user to AnonymousUser-class.
login_manager.anonymous_user = AnonymousUser


class Event(db.Model):
    """Database model for the events."""
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    signup_start = db.Column(db.DateTime)
    signup_end = db.Column(db.DateTime)
    limit = db.Column(db.Integer)

    def __repr__(self):
        return '<Event {}>'.format(self.id)


association_user_shift = db.Table('association',
                                  db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                                  db.Column('shift_id', db.Integer, db.ForeignKey('shifts.id')))


class Shift(db.Model):
    """Database model for shift that volunteers can attend."""
    __tablename__ = 'shifts'
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    limit = db.Column(db.Integer)
    volunteers = db.relationship('User', secondary=association_user_shift, backref='shifts')

    def __repr__(self):
        return '<Shift {}>'.format(self.id)


class Participate(db.Model):
    """Database model for the participates relation."""
    __tablename__ = 'events_users'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    seller_id = db.Column(db.String(20))

    def __repr__(self):
        return '<Participate {}>'.format(self.id)


class Email(db.Model):
    """Database model for sent emails."""
    __tablename__ = 'emails'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(JSON)
    events = db.relationship('EmailEvent', backref='email', lazy='dynamic')

    def __repr__(self):
        return '<Email {}>'.format(self.id)


class EmailEvent(db.Model):
    """Database model for transactional email events."""
    __tablename__ = 'emailevents'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), index=True)
    data = db.Column(JSON)
    email_id = db.Column(db.Integer, db.ForeignKey('emails.id'))

    def __repr__(self):
        return '<EmailEvent {}>'.format(self.id)
