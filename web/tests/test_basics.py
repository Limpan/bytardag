import pytest


def test_app_exists(app):
    assert app is not None


def test_app_is_testing(app):
    assert app.config['TESTING']


def test_home_page(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert 'Klädbytardagen'.encode() in rv.data
