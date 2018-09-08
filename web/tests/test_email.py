import pytest
from app import mail
from app.email import send_email
from flask_mail import Message
from requests import Response


def test_send_mail(mocker):
    mock_post = mocker.patch('requests.post')
    mock_post.return_value = mocker.MagicMock(spec=Response, status_code=200)
    send_email.apply(args=['test@example.com', 'Test email', 'main/email/test'], kwargs={'name': 'Pink'})
    assert mock_post.call_count == 1
