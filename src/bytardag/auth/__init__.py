from flask import Blueprint

bp = Blueprint("auth", __name__)

from bytardag.auth import routes  # noqa: E402, F401, I100, I202
