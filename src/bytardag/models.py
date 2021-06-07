"""Application data model."""
from flask_login import AnonymousUserMixin, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from bytardag import db, login_manager


class User(UserMixin, db.Model):
    """User account."""

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), index=True, unique=True)
    password_hash = db.Column(db.String(128), default=None)

    @property
    def password(self) -> None:
        """Write-only attribute."""
        raise AttributeError("Password is not a readable attribute.")

    @password.setter
    def password(self, password: str) -> None:
        """Password setter."""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        return check_password_hash(self.password_hash, password)


# Loads a user for given user_id.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class AnonymousUser(AnonymousUserMixin):
    """Class for anonymous user, which returns false for permission checks."""

    pass
