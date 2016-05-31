from flask import Response
from . import email
from .. import db
from ..models import Email, EmailEvent


@email.route('/webhook', methods=['GET'])
def webhook():
    """Webhook for transactional email events from Sendgrid."""
    # Store json data and add call process_event().
    return Response(200)
