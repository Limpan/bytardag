import pytest
import mock
from app.email import send_email
from celery.exceptions import Retry

@mock.patch('app.email.requests.post')
def test_sending_single_recipient_email(mock_post):
    mock_post.return_value.status_code = 202

    result = send_email('test@example.com', 'Test', 'main/email/test', name='Pink')
    assert result == True


@mock.patch('app.email.requests.post')
def test_retry_of_failed_email(mock_post):
    mock_post.return_value.status_code = 503

    with pytest.raises(Retry):
        result = send_email('test@example.com', 'Test', 'main/email/test', name='Pink')
