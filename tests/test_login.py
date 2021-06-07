from flask import url_for
from flask_login import current_user
import pytest
from bytardag.models import User
from sqlalchemy.exc import IntegrityError


def test_should_have_registration_route(client):
    assert 200 <= client.get(url_for("auth.register")).status_code < 400


def test_should_create_user_when_registering_new_user(client, db):
    """Should create new user when registering."""
    # Make sure there's no user in database.
    user_count = db.session.query(User).count()
    assert user_count == 0

    # Register new user
    rv = client.post(
        url_for("auth.register"),
        data=dict(
            email="test@example.com",
            password="secretsauce",
        ),
        follow_redirects=True,
    )

    # Check database for new user.
    user = db.session.query(User).filter_by(email="test@example.com").first()
    assert user


@pytest.mark.filterwarnings("ignore::sqlalchemy.exc.SAWarning")
def test_should_not_allow_to_create_user_with_duplicate_email(db):
    """Should not be allowed to add users with duplicate email."""
    user1 = User(email="test@example.com")
    user2 = User(email="test@example.com")
    db.session.add(user1)
    db.session.add(user2)

    with pytest.raises(IntegrityError):
        db.session.commit()


def test_should_be_able_to_login_with_credentials(client, db):
    """Should allow user to login with email and password."""
    user = User(email="test@example.com", password="secretsauce")
    db.session.add(user)
    db.session.commit()

    # Login user
    rv = client.post(
        url_for("auth.login"),
        data=dict(
            email="test@example.com",
            password="secretsauce",
            remember_me=False,
        ),
        follow_redirects=True,
    )

    assert current_user == user

@pytest.mark.parametrize("email", ["test@example.com"])
@pytest.mark.usefixtures("authenticated_as_user")
def test_should_be_able_to_logout(client, db):
    assert current_user.email == "test@example.com"