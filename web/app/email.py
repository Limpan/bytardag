from celery.utils.log import get_task_logger
from celery.exceptions import Retry
from sqlalchemy.orm.exc import NoResultFound
from flask import current_app, render_template
from flask_mail import Message
from . import create_celery_app
from . import mail

celery = create_celery_app()
logger = get_task_logger(__name__)


@celery.task
def send_email(to, subject, template, **kwargs):
    """Function for sending emails."""
    app = current_app._get_current_object()
    msg = Message(app.config['BYTARDAG_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['BYTARDAG_MAIL_SENDER'], recipients=[to], charset='utf-8')
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    logger.debug('Sending email through: ' + app.config['MAIL_SERVER'])
    try:
        mail.send(msg)
    except:
        logger.error('Failed to send email to {email}'.format(email=msg.recipients))
    # TODO: Add code to handle exceptions.
