import pytest
#from flask import url_for
from app.models import User
from app import mail


def test_login_and_logout(client, db):
    # Add test user.
    user = User(email='test@example.com', password='secretsauce', confirmed=True)
    db.session.add(user)
    db.session.commit()

    # Login
    rv = client.post('/auth/login', data=dict(
        email='test@example.com',
        password='secretsauce'
    ), follow_redirects=True)
    assert 'Du är nu inloggad.'.encode() in rv.data

    # Logout
    rv = client.post('/auth/logout', follow_redirects=True)
    assert 'Du är nu utloggad.'.encode() in rv.data

    #Correct email, wrong password
    rv = client.post('/auth/login', data=dict(
        email='test@example.com',
        password='ihavenoclue'
    ), follow_redirects=True)
    assert 'Fel användarnamn eller lösenord.'.encode() in rv.data

    # Wrong email, correct password
    rv = client.post('/auth/login', data=dict(
        email='testx@example.com',
        password='secretsauce'
    ), follow_redirects=True)
    assert 'Fel användarnamn eller lösenord.'.encode() in rv.data


def test_password_recovery(client, db, mocker):
    mock_send_email = mocker.patch('app.email.send_email')

    # Add test user.
    user = User(email='test@example.com', password='forgotten', confirmed=True)
    db.session.add(user)
    db.session.commit()

    rv = client.post('/auth/reset', data=dict(
        email='test@example.com'
    ))
