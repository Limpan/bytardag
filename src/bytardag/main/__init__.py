from flask import Blueprint

bp = Blueprint("main", __name__)

from bytardag.main import routes  # noqa: E402, F401, I100, I202
