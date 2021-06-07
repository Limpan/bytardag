from flask import url_for
import pytest

from bytardag import __version__


def test_should_have_correct_version_string():
    assert __version__ == "0.1.0"


def test_should_have_an_app_object(app):
    assert app is not None


def test_should_be_in_testing_mode(app):
    assert app.config["TESTING"]


def test_should_return_an_index_page(client):
    assert 200 <= client.get(url_for("main.index")).status_code < 400
