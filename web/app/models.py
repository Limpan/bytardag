from flask import current_app, request, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from app.exceptions import ValidationError
from datetime import datetime, time
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import hashlib

"""Add database model, see example in
https://github.com/miguelgrinberg/flasky/blob/master/app/models.py
"""

def db_key():
    """Return encryption key for database."""
    return current_app.config['DB_ENCRYPTION_KEY']


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
    email = db.Column(db.String(254), unique=True, index=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    password_hash = db.Column(db.String(128), default=None)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)
    gdpr_consent = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(32))
    account = db.relationship('BankAccount', uselist=False, backref='user')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    events = db.relationship('Attendance', back_populates='user')

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

    def generate_confirmation_token(self, expiration=3600):
        """Used to generate a token for email confirmation."""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')


    @staticmethod
    def confirm_account(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        user = User.query.filter_by(id=data.get('confirm')).first()
        if not user:
            return False
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        return True


    def confirm(self, token):
        """Used to verify a token for email confirmation."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_token(self, expiration=3600):
        """Used to generate a token for a password reset."""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

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

    @property
    def profile_complete(self):
        return self.first_name and self.last_name

    @profile_complete.setter
    def profile_complete(self, value):
        raise AttributeError('profile_complete is not a writable attribute.')

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


class BankAccount(db.Model):
    """Database model for bank accounts."""
    __tablename__ = 'bank_accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    bank = db.Column(EncryptedType(db.String(64),
                                   db_key,
                                   AesEngine,
                                   'pkcs5'))
    clearing = db.Column(EncryptedType(db.String(16),
                                       db_key,
                                       AesEngine,
                                       'pkcs5'))
    _number = db.Column(EncryptedType(db.String(64),
                                      db_key,
                                      AesEngine,
                                      'pkcs5'))

    @staticmethod
    def _obfuscate(value):
        if not value is None:
            return '*' * (len(value) - 2) + value[-2:]
        return None

    @hybrid_property
    def number(self):
        return BankAccount._obfuscate(self._number)

    @number.setter
    def number(self, value):
        self._number = value

    @number.expression
    def number(cls):
        return cls._number


class Event(db.Model):
    """Database model for the events."""
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    signup_start = db.Column(db.DateTime)
    signup_end = db.Column(db.DateTime)
    limit = db.Column(db.Integer)
    attendees = db.relationship('Attendance', back_populates='event', order_by='Attendance.seller_id')
    next_seller_id = db.Column(db.Integer, default=0)


    @staticmethod
    def insert_event():
        from datetime import datetime

        event = Event(start=datetime(2016, 10, 1, 8, 0),
                      end=datetime(2016, 10, 1, 12, 0),
                      signup_start=datetime(2016, 9, 11, 7, 0),
                      signup_end=datetime(2016, 9, 25, 0, 0),
                      limit=125,
                      next_seller_id=1)
        db.session.add(event)
        db.session.commit()

    @staticmethod
    def generate_seller_id(i):
        """Generate seller ids from integer."""
        chars = 'ABCEFGHJKLMNOPRSTVXZ'
        return '{}-{:02}'.format(chars[i % 20], i // 20 % 100 * 2 + 1)


    def signup_open(self):
        now = datetime.utcnow()
        return self.signup_start < now and now < self.signup_end and len(self.attendees) < self.limit

    def signup_over(self):
        now = datetime.utcnow()
        return now >= self.signup_end or len(self.attendees) >= self.limit

    def __repr__(self):
        return '<Event {}>'.format(self.id)


def get_current_event():
    event = Event.query.filter(Event.start > datetime.utcnow()).order_by(Event.start).first()
    if not event:
        event = Event.query.order_by(Event.start).first()
    return event


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

class Attendance(db.Model):
    """Database model for the attendance relation, implemented as an
    association object.

    Association object pattern:
    http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#association-object
    """
    __tablename__ = 'attendance'
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    seller_id = db.Column(db.String(20), default='')
    user = db.relationship('User', back_populates='events')
    event = db.relationship('Event', back_populates='attendees')

    def __repr__(self):
        return '<Attendance; event {}, user {}>'.format(self.event_id, self.user.email)
