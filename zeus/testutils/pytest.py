from __future__ import absolute_import

import os
import pytest

from sqlalchemy import event
from sqlalchemy.orm import Session

from zeus.config import alembic, create_app, db
from zeus.storage.mock import FileStorageCache


@pytest.fixture(scope='session')
def session_config(request):
    return {
        'db_name': 'test_zeus',
    }


@pytest.fixture(scope='session')
def app(request, session_config):
    app = create_app(
        _read_config=False,
        SQLALCHEMY_DATABASE_URI='postgresql:///' + session_config['db_name'],
        DEFAULT_FILE_STORAGE='zeus.storage.mock.FileStorageCache',
    )
    print('here')

    app_context = app.test_request_context()
    context = app_context.push()

    # request.addfinalizer(app_context.pop)
    return app


@pytest.fixture(scope='session', autouse=True)
def setup_db(request, app, session_config):
    db_name = session_config['db_name']
    # 9.1 does not support --if-exists
    if os.system("psql -l | grep '%s'" % db_name) == 0:
        assert not os.system('dropdb %s' % db_name)
    assert not os.system('createdb -E utf-8 %s' % db_name)

    alembic.upgrade()

    @event.listens_for(Session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    # TODO: find a way to kill db connections so we can dropdob
    # def teardown():
    #     os.system('dropdb %s' % db_name)
    # request.addfinalizer(teardown)


@pytest.fixture(autouse=True)
def db_session(request):
    request.addfinalizer(db.session.remove)

    db.session.begin_nested()


def pytest_runtest_setup(item):
    FileStorageCache.clear()
