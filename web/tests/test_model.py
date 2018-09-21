import pytest
from app.models import BankAccount, User
from sqlalchemy.sql import text


def test_password_setter():
    u = User(password='supersecret')
    assert u.password_hash is not None


def test_no_password_getter():
    u = User(password='supersecret')
    with pytest.raises(AttributeError):
        u.password


def test_password_verification():
    u = User(password='cat')
    assert u.verify_password('cat')
    assert u.verify_password('dog') is False


def test_password_salts_are_random():
    u = User(password='cat')
    u2 = User(password='cat')
    assert u.password_hash != u2.password_hash


def test_bank_account_number_masking():
    a1 = BankAccount(clearing='4386', number='9823857')
    assert a1.clearing == '4386'
    assert a1.number == '*****57'
    assert a1._number == '9823857'

    a2 = BankAccount(clearing='573', number='39923456')
    assert a2.clearing == '573'
    assert a2.number == '******56'
    assert a2._number == '39923456'

def test_bank_account_not_stored_in_the_clear(db):
    user = User()
    account = BankAccount(bank='JVA Bank', clearing='1234', number='9876543')
    user.account = account
    db.session.add(user)
    db.session.commit()

    sql = text('SELECT bank, clearing, _number FROM bank_accounts WHERE id=:id')
    result = db.session.execute(sql, {'id': user.account.id})
    assert result.rowcount is 1

    row = result.next()

    assert not row['bank'] is account.bank
    assert not row['clearing'] is account.clearing
    assert not row['_number'] is account._number
