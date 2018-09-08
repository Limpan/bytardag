from celery.utils.log import get_task_logger
from celery.exceptions import Retry
from sqlalchemy.orm.exc import NoResultFound
from flask import current_app, render_template
from flask_mail import Message
from . import create_celery_app
from . import sentry
#from . import mail
import requests


celery = create_celery_app()
logger = get_task_logger(__name__)


# @celery.task
# def send_email(to, subject, template, **kwargs):
#     """Function for sending emails."""
#     app = current_app._get_current_object()
#     msg = Message(app.config['BYTARDAG_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
#                   sender=app.config['BYTARDAG_MAIL_SENDER'],
#                   reply_to=app.config['BYTARDAG_MAIL_REPLY_TO'],
#                   recipients=[to], charset='utf-8')
#     msg.body = render_template(template + '.txt', **kwargs)
#     msg.html = render_template(template + '.html', **kwargs)
#     logger.debug('Sending email to {recipient} with {server}.'.format(recipient=to, server=app.config['MAIL_SERVER']))
#     try:
#         mail.send(msg)
#     except Exception as e:
#         logger.error('Failed to send email to {email}'.format(email=msg.recipients), exc_info=1)
#         # TODO: Add code to handle exceptions.


@celery.task(bind=True, max_retries=5, soft_time_limit=5)
def send_email(self, to, subject, template, **kwargs):
    """Function for sending email with Sendgrid Web API."""
    app = current_app._get_current_object()
    url = app.config['SENDGRID_APIURL'] + 'mail/send'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + app.config['SENDGRID_APIKEY']
    }
    data = {
        "personalizations": [
            {
                "to": [{"email": to}],
                "subject": app.config['BYTARDAG_MAIL_SUBJECT_PREFIX'] + ' ' + subject
            }
        ],
        "from": {
            "email": app.config['BYTARDAG_MAIL_SENDER_ADDRESS'],
            "name": app.config['BYTARDAG_MAIL_SENDER_NAME']
        },
        "content": [
            {
                "type": "text/plain",
                "value": render_template(template + '.txt', **kwargs)
            },
            {
                "type": "text/html",
                "value": render_template(template + '.html', **kwargs)
            }
        ]
    }

    if app.config.get('MAIL_SUPPRESS_SEND', False) or app.testing:
        data['mail_settings'] = { "sandbox_mode": True }

    logger.debug('Attempting to send email to %s.' % to)
    try:
        rv = requests.post(url, headers=headers, json=data)
    except Exception as e:
        logger.error('Failed to send email to %s.' % to)
    else:
        if 200 <= rv.status_code < 400:
            logger.debug('Email succesfully sent to %s.' % to)
        if 400 <= rv.status_code < 500:
            logger.error('Sendgrid request returned status %s (%s).' % (rv.status_code, to))
        if 500 <= rv.status_code < 600:
            logger.warning('Sendgrid request returned status %s (%s)' % (rv.status_code, to))
            sentry.captureException()
            self.retry(countdown=10)
