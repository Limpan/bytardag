import pytest
from app.models import User


def test_password_setter():
    u = User(password='supersecret')
    assert u.password_hash is not None


def test_no_password_getter():
    u = User(password='supersecret')
    with pytest.raises(AttributeError):
        u.password


def test_password_verification():
    u = User(password='cat')
    assert u.verify_password('cat')
    assert u.verify_password('dog') is False


def test_password_salts_are_random():
    u = User(password='cat')
    u2 = User(password='cat')
    assert u.password_hash != u2.password_hash
