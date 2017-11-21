import os
import pytest

from sqlalchemy import event
from sqlalchemy.orm import Session

from zeus import config
from zeus.storage.mock import FileStorageCache


@pytest.fixture(scope='session')
def session_config(request):
    return {
        'db_name': 'test_zeus',
    }


@pytest.fixture(scope='session')
def app(request, session_config):
    app = config.create_app(
        _read_config=False,
        SQLALCHEMY_DATABASE_URI='postgresql:///' + session_config['db_name'],
        FILE_STORAGE={
            'backend': 'zeus.storage.mock.FileStorageCache',
        },
        SECRET_KEY=os.urandom(24),
        GITHUB_CLIENT_ID='github.client-id',
        GITHUB_CLIENT_SECRET='github.client-secret',
        MAIL_SUPPRESS_SEND=True,
        NPLUSONE_RAISE=True,
    )
    app.testing = True
    yield app


@pytest.fixture(scope='session', autouse=True)
def db(request, app, session_config):
    db_name = session_config['db_name']
    with app.app_context():
        # Postgres 9.1 does not support --if-exists
        if os.system("psql -l | grep '%s'" % db_name) == 0:
            assert not os.system('dropdb %s' % db_name)
        assert not os.system('createdb -E utf-8 %s' % db_name)

        config.alembic.upgrade()

        # TODO: need to kill db connections in order to drop database
        #     config.db.drop_all()
        #     os.system('dropdb %s' % db_name)
        return config.db


@event.listens_for(Session, "after_transaction_end")
def restart_savepoint(session, transaction):
    if transaction.nested and not transaction._parent.nested:
        session.begin_nested()


@pytest.fixture(scope='function')
def req_ctx(request, app):
    with app.test_request_context() as req_ctx:
        yield req_ctx


@pytest.fixture(scope='function', autouse=True)
def db_session(request, req_ctx, db):
    db.session.begin_nested()

    yield db.session

    # transaction.rollback()
    # connection.close()
    # db.session.remove()


@pytest.fixture(scope='function', autouse=True)
def filestorage(app):
    FileStorageCache.clear()

    yield FileStorageCache


@pytest.fixture(scope='function', autouse=True)
def redis(app):
    config.redis.flushdb()
    yield config.redis


@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='function', autouse=True)
def outbox(app):
    with config.mail.record_messages() as ob:
        yield ob


@pytest.fixture
def private_key():
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend

    return rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=2048)


@pytest.fixture
def public_key(private_key):
    return private_key.public_key()


@pytest.fixture
def public_key_bytes(public_key):
    from cryptography.hazmat.primitives import serialization
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
