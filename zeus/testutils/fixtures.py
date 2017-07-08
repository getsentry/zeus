import os
import pytest

from datetime import datetime, timedelta

from zeus import factories, models
from zeus.constants import Result, Status


DATA_FIXTURES = os.path.join(os.path.dirname(
    __file__), os.pardir, os.pardir, 'tests', 'fixtures')


@pytest.fixture(scope='function')
def default_user(db_session):
    r = factories.UserFactory(
        email='foo@example.com',
    )
    db_session.add(r)
    db_session.commit()
    return r


@pytest.fixture(scope='function')
def default_login(client, default_user):
    with client.session_transaction() as session:
        session['uid'] = default_user.id.hex

    yield default_user


@pytest.fixture(scope='function')
def default_repo(db_session):
    r = factories.RepositoryFactory(
        url='https://github.com/getsentry/zeus.git',
        backend=models.RepositoryBackend.git,
        status=models.RepositoryStatus.active,
    )
    db_session.add(r)
    db_session.commit()
    return r


@pytest.fixture(scope='function')
def default_repo_access(db_session, default_repo, default_user):
    access = models.RepositoryAccess(
        user_id=default_user.id,
        repository_id=default_repo.id,
    )
    db_session.add(access)
    db_session.commit()

    return access


@pytest.fixture(scope='function')
def default_revision(db_session, default_repo):
    r = factories.RevisionFactory(
        repository=default_repo,
        sha='884ea9e17b53933febafd7e02d8bd28f3c9d479d',
    )
    db_session.add(r)
    db_session.commit()
    return r


@pytest.fixture(scope='function')
def default_source(db_session, default_revision):
    r = factories.SourceFactory(
        repository=default_revision.repository,
        revision_sha=default_revision.sha,
    )
    db_session.add(r)
    db_session.commit()
    return r


@pytest.fixture(scope='function')
def default_build(db_session, default_repo, default_source):
    r = factories.BuildFactory(
        repository=default_repo,
        source=default_source,
        date_started=datetime.utcnow() - timedelta(minutes=6),
        date_finished=datetime.utcnow(),
        result=Result.passed,
        status=Status.finished,
    )
    db_session.add(r)
    db_session.commit()
    return r


@pytest.fixture(scope='function')
def default_job(db_session, default_build):
    r = factories.JobFactory(
        repository=default_build.repository,
        build=default_build,
        date_started=datetime.utcnow() - timedelta(minutes=6),
        date_finished=datetime.utcnow(),
        result=Result.passed,
        status=Status.finished,
    )
    db_session.add(r)
    db_session.commit()
    return r


@pytest.fixture(scope='function')
def default_artifact(db_session, default_job):
    r = factories.ArtifactFactory(
        repository=default_job.repository,
        job=default_job,
    )
    db_session.add(r)
    db_session.commit()
    return r


@pytest.fixture(scope='session')
def sample_xunit():
    with open(os.path.join(DATA_FIXTURES, 'sample-xunit.xml')) as fp:
        return fp.read()


@pytest.fixture(scope='session')
def sample_xunit_with_artifacts():
    with open(os.path.join(DATA_FIXTURES, 'sample-xunit-with-artifacts.xml')) as fp:
        return fp.read()


@pytest.fixture(scope='session')
def sample_cobertura():
    with open(os.path.join(DATA_FIXTURES, 'sample-cobertura.xml')) as fp:
        return fp.read()


@pytest.fixture(scope='session')
def sample_jacoco():
    with open(os.path.join(DATA_FIXTURES, 'sample-jacoco.xml')) as fp:
        return fp.read()
