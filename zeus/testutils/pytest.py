import os
import pytest
import responses

from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy.testing import assertions, assertsql

from zeus import auth, config
from zeus.storage.mock import FileStorageCache


class CountStatementsWithDebug(assertsql.AssertRule):
    def __init__(self, count):
        self.count = count
        self.statements = []

    # TODO(dcramer): it'd be nice to capture the last in_app frame here
    # TODO(dcramer): even better, it'd be nice to snapshot network requests
    # similar to Jest, and just ensure they havent changed
    def process_statement(self, execute_observed):
        self.statements.extend(execute_observed.statements)

    def no_more_statements(self):
        statement_count = len(self.statements)
        if self.count != statement_count:
            assert False, "desired statement count %d does not match %d:\n%s" % (
                self.count,
                statement_count,
                "\n".join(
                    ("  {}. {}".format(k + 1, v) for k, v in enumerate(self.statements))
                ),
            )


class AssertionHelper(object):
    def __init__(self, db):
        self.db = db
        self.mgr = assertions.AssertsExecutionResults()

    def assert_statement_count(self, count):
        return self.mgr.assert_execution(
            self.db.engine, CountStatementsWithDebug(count)
        )


@pytest.fixture(scope="session")
def session_config(request):
    return {"db_name": "test_zeus", "db_host": "127.0.0.1", "db_user": "postgres"}


@pytest.fixture(scope="session")
def app(request, session_config):
    app = config.create_app(
        _read_config=False,
        SQLALCHEMY_DATABASE_URI="postgresql://{}@{}/{}".format(
            session_config["db_user"],
            session_config["db_host"],
            session_config["db_name"],
        ),
        FILE_STORAGE={"backend": "zeus.storage.mock.FileStorageCache"},
        SECRET_KEY=os.urandom(24),
        GITHUB_CLIENT_ID="github.client-id",
        GITHUB_CLIENT_SECRET="github.client-secret",
        MAIL_SUPPRESS_SEND=True,
        NPLUSONE_RAISE=True,
    )
    app.testing = True
    yield app


@pytest.fixture(scope="session", autouse=True)
def db(request, app, session_config):
    db_name = session_config["db_name"]
    db_host = session_config["db_host"]
    db_user = session_config["db_user"]
    with app.app_context():
        # Postgres 9.1 does not support --if-exists
        if (
            os.system(
                "psql -U {} -h {} -l | grep '{}'".format(db_user, db_host, db_name)
            )
            == 0
        ):
            assert not os.system(
                "dropdb -U {} -h {} {}".format(db_user, db_host, db_name)
            )
        assert not os.system(
            "createdb -U {} -E utf-8 -h {} {}".format(db_user, db_host, db_name)
        )

        config.alembic.upgrade()

        # TODO: need to kill db connections in order to drop database
        #     config.db.drop_all()
        #     os.system('dropdb %s' % db_name)
        return config.db


@pytest.fixture(scope="session")
def sqla_assertions(db):
    return AssertionHelper(db)


@event.listens_for(Session, "after_transaction_end")
def restart_savepoint(session, transaction):
    if transaction.nested and not transaction._parent.nested:
        session.begin_nested()


@pytest.fixture(scope="function")
def req_ctx(request, app):
    with app.test_request_context() as req_ctx:
        yield req_ctx


@pytest.fixture(scope="function", autouse=True)
def db_session(request, req_ctx, db):
    db.session.begin_nested()

    yield db.session


# transaction.rollback()
# connection.close()
# db.session.remove()


@pytest.fixture(scope="function", autouse=True)
def filestorage(app):
    FileStorageCache.clear()

    yield FileStorageCache


@pytest.fixture(scope="function", autouse=True)
def redis(app):
    config.redis.flushdb()
    yield config.redis


@pytest.fixture(scope="function")
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function", autouse=True)
def outbox(app):
    with config.mail.record_messages() as ob:
        yield ob


@pytest.fixture
def private_key():
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend

    return rsa.generate_private_key(
        backend=default_backend(), public_exponent=65537, key_size=2048
    )


@pytest.fixture
def public_key(private_key):
    return private_key.public_key()


@pytest.fixture
def public_key_bytes(public_key):
    from cryptography.hazmat.primitives import serialization

    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


@pytest.fixture
def default_tenant(default_repo):
    auth.set_current_tenant(auth.RepositoryTenant(repository_id=default_repo.id))


@pytest.fixture
def mock_vcs_server():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps.add(responses.GET, "http://localhost:8070/stmt/log", json={"log": []})
        rsps.add(
            responses.GET,
            "http://localhost:8070/stmt/branches",
            json={"branches": ["master"]},
        )
        yield
