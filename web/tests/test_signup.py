import pytest
from flask import url_for
from app.models import Event, User, get_current_event
from datetime import datetime, timedelta


def test_signup(client, db):
    user = User(email='test@example.com',
                password='secretsauce',
                first_name='Clark',
                last_name='Kent',
                confirmed=True)
    db.session.add(user)

    now = datetime.utcnow()
    event = Event(start=now + timedelta(days=14),
                  end=now + timedelta(days=14, hours=4),
                  signup_start=now - timedelta(hours=24),
                  signup_end=now + timedelta(hours=24),
                  limit=5,
                  next_seller_id=1)
    db.session.add(event)
    db.session.commit()

    event_id = event.id

    # Login
    rv = client.post('/auth/login', data=dict(
        email='test@example.com',
        password='secretsauce'
    ), follow_redirects=True)

    # Sign up
    rv = client.post('/', data={'signup': 'x'}, follow_redirects=True)

    assert rv.status_code == 200
    assert 'Grattis! Du är nu anmäld.'.encode() in rv.data

    event = Event.query.get(event_id)
    assert len(event.attendees) == 1
    assert len(user.events) == 1
    assert user.events[0].event == event


def test_signup_not_open(client, db):
    user = User(email='test@example.com',
                password='secretsauce',
                first_name='Clark',
                last_name='Kent',
                confirmed=True)
    db.session.add(user)

    now = datetime.utcnow()
    event = Event(start=now + timedelta(days=14),
                  end=now + timedelta(days=14, hours=4),
                  signup_start=now + timedelta(hours=24),
                  signup_end=now + timedelta(hours=48),
                  limit=5,
                  next_seller_id=1)
    db.session.add(event)
    db.session.commit()

    event_id = event.id

    # Login
    rv = client.post('/auth/login', data=dict(
        email='test@example.com',
        password='secretsauce'
    ), follow_redirects=True)

    # Sign up
    rv = client.post('/', data={'signup': 'x'}, follow_redirects=True)

    event = Event.query.get(event_id)
    assert len(event.attendees) == 0
    assert len(user.events) == 0


def test_signup_not_open(client, db):
    user = User(email='test@example.com',
                password='secretsauce',
                first_name='Clark',
                last_name='Kent',
                confirmed=True)
    db.session.add(user)

    now = datetime.utcnow()
    event = Event(start=now + timedelta(days=14),
                  end=now + timedelta(days=14, hours=4),
                  signup_start=now - timedelta(hours=48),
                  signup_end=now - timedelta(hours=24),
                  limit=5,
                  next_seller_id=1)
    db.session.add(event)
    db.session.commit()

    event_id = event.id

    # Login
    rv = client.post('/auth/login', data=dict(
        email='test@example.com',
        password='secretsauce'
    ), follow_redirects=True)

    # Sign up
    rv = client.post('/', data={'signup': 'x'}, follow_redirects=True)

    event = Event.query.get(event_id)
    assert len(event.attendees) == 0
    assert len(user.events) == 0


def test_signup_full(client, db):
    now = datetime.utcnow()
    event = Event(start=now + timedelta(days=14),
                  end=now + timedelta(days=14, hours=4),
                  signup_start=now - timedelta(hours=24),
                  signup_end=now + timedelta(hours=24),
                  limit=5,
                  next_seller_id=1)
    db.session.add(event)
    db.session.commit()

    for i in range(5):
        user = User(email='test{}@example.com'.format(i),
                    password='secretsauce',
                    first_name='Clark',
                    last_name='Kent',
                    confirmed=True)
        db.session.add(user)
        db.session.commit()

        # Login
        rv = client.post('/auth/login', data=dict(
            email='test{}@example.com'.format(i),
            password='secretsauce'
        ), follow_redirects=True)

        # Sign up
        rv = client.post('/', data={'signup': 'x'}, follow_redirects=True)

        # Logout
        rv = client.post('/auth/logout', follow_redirects=True)

    user = User(email='test@example.com',
                password='secretsauce',
                first_name='Clark',
                last_name='Kent',
                confirmed=True)
    db.session.add(user)
    db.session.commit()

    event_id = event.id

    # Login
    rv = client.post('/auth/login', data=dict(
        email='test@example.com',
        password='secretsauce'
    ), follow_redirects=True)

    # Sign up
    rv = client.post('/', data={'signup': 'x'}, follow_redirects=True)

    event = Event.query.get(event_id)
    assert len(event.attendees) == 5
    assert not user in event.attendees
