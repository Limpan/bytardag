from celery.utils.log import get_task_logger
from celery.exceptions import Retry
from sqlalchemy.orm.exc import NoResultFound
from flask import render_template
from flask_mail import Message
from .. import create_celery_app
from .. import db
from ..models import User

celery = create_celery_app()
logger = get_task_logger(__name__)


@celery.task
def send_email(to, subject, template, **kwargs):
    """Function for sending emails."""
#    app = current_app._get_current_object()
#    msg = Message(app.config['CHRONOS_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
#                  sender=app.config['CHRONOS_MAIL_SENDER'], recipients=[to], charset='utf-8')
#    msg.body = render_template(template + '.txt', **kwargs)
#    msg.html = render_template(template + '.html', **kwargs)
#    # Sends email using another thread than the flask instance to be able to send it async.
#    thr = Thread(target=send_async_email, args=[app, msg])
#    thr.start()
#    return thr
    pass


@celery.task
def process_event(id):
    """Process Sendgrid webhook event."""
    pass
