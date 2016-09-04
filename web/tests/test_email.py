import pytest
from app import mail
from app.email import send_email


def test_sending_single_recipient_email():
    with mail.record_messages() as outbox:
        send_email('test@example.com', 'Test email', 'main/email/test', name='Pink')
        assert len(outbox) == 1
        assert len(outbox[0].recipients) == 1
        assert outbox[0].recipients[0] == 'test@example.com'
        assert outbox[0].subject == '[bytardag.se] Test email'
        assert 'Mr. Pink' in outbox[0].html
        assert 'Mr. Pink' in outbox[0].body
