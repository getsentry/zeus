import os
import pytest

from datetime import datetime, timedelta

from zeus import models
from zeus.constants import Result, Status

DATA_FIXTURES = os.path.join(os.path.dirname(
    __file__), os.pardir, os.pardir, 'tests', 'fixtures')


@pytest.fixture(scope='function')
def default_user(db_session):
    user = models.User(
        email='foo@example.com',
    )
    db_session.add(user)
    db_session.commit()

    return user


@pytest.fixture(scope='function')
def default_login(client, default_user):
    with client.session_transaction() as session:
        session['uid'] = default_user.id.hex

    yield default_user


@pytest.fixture(scope='function')
def default_repo(db_session):
    repo = models.Repository(
        url='https://github.com/getsentry/zeus.git',
        backend=models.RepositoryBackend.git,
        status=models.RepositoryStatus.active,
    )
    db_session.add(repo)
    db_session.commit()

    return repo


@pytest.fixture(scope='function')
def default_revision(db_session, default_repo):
    revision = models.Revision(
        repository_id=default_repo.id,
        sha='884ea9e17b53933febafd7e02d8bd28f3c9d479d',
    )
    db_session.add(revision)
    db_session.commit()

    return revision


@pytest.fixture(scope='function')
def default_source(db_session, default_revision):
    source = models.Source(
        repository_id=default_revision.repository_id,
        revision_sha=default_revision.sha,
    )
    db_session.add(source)
    db_session.commit()

    return source


@pytest.fixture(scope='function')
def default_build(db_session, default_repo, default_source):
    build = models.Build(
        repository_id=default_repo.id,
        source_id=default_source.id,
        date_started=datetime.utcnow() - timedelta(minutes=6),
        date_finished=datetime.utcnow(),
        result=Result.passed,
        status=Status.finished,
    )
    db_session.add(build)
    db_session.commit()

    return build


@pytest.fixture(scope='function')
def default_repo_access(db_session, default_repo, default_user):
    access = models.RepositoryAccess(
        user_id=default_user.id,
        repository_id=default_repo.id,
    )
    db_session.add(access)
    db_session.commit()

    return access


@pytest.fixture(scope='session')
def sample_xunit():
    with open(os.path.join(DATA_FIXTURES, 'sample-xunit.xml')) as fp:
        return fp.read()
