from celery.utils.log import get_task_logger
from celery.exceptions import Retry
from sqlalchemy.orm.exc import NoResultFound
from flask import current_app, render_template
from flask_mail import Message
from . import create_celery_app
from . import mail
import requests
import json


celery = create_celery_app()
logger = get_task_logger(__name__)


@celery.task(bind=True, soft_time_limit=5)
def send_email(self, to_addr, subject, template, **kwargs):
    app = current_app
    host = 'https://api.sendgrid.com/v3/'
    apikey = app.config['SENDGRID_APIKEY']
    from_addr = app.config['BYTARDAG_MAIL_SENDER']

    data = {
        'personalizations': [{
            'to': [{
                'email': to_addr}],
                'subject': subject}],
        'from': { 'email': from_addr},
        'content': [{
            'type': 'text/plain',
            'value': render_template(template + '.html', **kwargs)}]}

    result = requests.post('{host}mail/send'.format(host=host),
                           json.dumps(data),
                           headers={'Authorization': 'Bearer {apikey}'.format(apikey=apikey),
                                    'Content-type': 'application/json'})

    if result.status_code in [200, 202]:
        # All is well
        logger.info('Email with subject (%s) successfully sent to %s.' % (subject, to_addr))
        return True

    if result.status_code in [500, 503]:
        # Sendgrid messed up, retry in a while
        logger.info('Email sending failed (to: %s), retrying in a while...' % (to_addr))
        raise self.retry(countdown = 60 * 3)

    # Something broken, will not retry
    logger.error('Email sending failed with status code %s and message %s.' % (result.status_code, result.json))
