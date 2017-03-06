import pytest
from app import create_app
from app import db as _db
from app.models import Role


@pytest.fixture(scope='session')
def app(request):
    """Create an application context."""
    app = create_app('testing')
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)

    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session wide database connection."""
    _db.init_app(app)
    _db.create_all()
    _db.session.commit()
    Role.insert_roles()

    def teardown():
        _db.session.close_all()
        _db.drop_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function', autouse=True)
def session(db, request):
    """Create a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session
