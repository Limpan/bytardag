from flask import url_for
import pytest

from bytardag import __version__


def test_version():
    assert __version__ == "0.1.0"


def test_app_exists(app):
    assert app is not None


def test_app_is_testing(app):
    assert app.config["TESTING"]


def test_index_page(client):
    assert 200 <= client.get(url_for("main.index")).status_code < 400
