from flask import Blueprint

# Initialization of email blueprint.
email = Blueprint('email', __name__)

from . import views
