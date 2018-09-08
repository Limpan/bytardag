import pytest
from flask import url_for
from app.models import User


def test_register_new_user_and_confirmation(client, db, mocker):
    mock_send_email = mocker.patch('app.email.send_email')

    # Register new user
    rv = client.post('auth/register', data=dict(
        email='test@example.com',
        password='secretsauce',
        first_name='Clark',
        last_name='Kent'
    ), follow_redirects=True)

    # Check database for new user.
    new_user = db.session.query(User).filter_by(email='test@example.com').first()
    assert new_user
    assert not new_user.confirmed

    # Verify email is being sent.
    assert mock_send_email.delay.called

    # Use the generated token and confirm the account
    token = mock_send_email.delay.call_args[1]['token']
    rv = client.get('auth/confirm/' + token, follow_redirects=True)

    # Check that account is confirmed
    new_user = db.session.query(User).filter_by(email='test@example.com').first()
    assert new_user.confirmed


def test_unconfirmed_account(client, db):
    # Register new user
    rv = client.post('auth/register', data=dict(
        email='test@example.com',
        password='secretsauce',
        first_name='Clark',
        last_name='Kent'
    ), follow_redirects=True)

    rv = client.get('profile', follow_redirects=True)
    assert 'Din epostadress har inte bekräftats.'.encode() in rv.data

    user = db.session.query(User).filter_by(email='test@example.com').first()
    user.confirmed = True
    db.session.commit()

    rv = client.get('profile', follow_redirects=True)
    assert 'Din profil'.encode() in rv.data
