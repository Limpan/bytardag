import pytest
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from flask import url_for
import re

from app import mail


@pytest.mark.skip(reason='fix in the future')
def test_password_reset_email(client):
    # response = client.get(url_for('auth.password_reset_request'))
    with mail.record_messages() as outbox:
        response = client.post(url_for('auth.password_reset_request'),
                               data=dict(email='hugo@hugolundin.se'))
        # assert response.status_code == 200
        assert len(outbox) == 1
        assert outbox[0].subject == '[Chronos] Reset password'
        assert 'Hugo' in outbox[0].html

        token = re.search(r'reset\/(.*)"', outbox[0].html).group(1)

        response = client.post(url_for('auth.password_reset', token=token),
                               data=dict(email='hugo@hugolundin.se',
                               password='1q2w3e4r', password2='1q2w3e4r'))
        assert response.status_code == 302

        response = client.post(url_for('auth.login'),
                               data=dict(email='hugo@hugolundin.se',
                               password='1q2w3e4r'),
                               follow_redirects=True)
        assert response.status_code == 200
