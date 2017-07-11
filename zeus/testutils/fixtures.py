import os
import pytest

from datetime import datetime, timedelta

from zeus import factories, models
from zeus.constants import Result, Status

DATA_FIXTURES = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'tests', 'fixtures')


@pytest.fixture(scope='function')
def default_user():
    return factories.UserFactory(
        email='foo@example.com',
    )


@pytest.fixture(scope='function')
def default_login(client, default_user):
    with client.session_transaction() as session:
        session['uid'] = default_user.id.hex

    yield default_user


@pytest.fixture(scope='function')
def default_repo():
    return factories.RepositoryFactory(
        url='https://github.com/getsentry/zeus.git',
        backend=models.RepositoryBackend.git,
        status=models.RepositoryStatus.active,
    )


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
def default_revision(default_repo):
    return factories.RevisionFactory(
        repository=default_repo,
        sha='884ea9e17b53933febafd7e02d8bd28f3c9d479d',
    )


@pytest.fixture(scope='function')
def default_source(default_revision):
    return factories.SourceFactory(
        revision=default_revision,
    )


@pytest.fixture(scope='function')
def default_build(default_source):
    return factories.BuildFactory(
        source=default_source,
        date_started=datetime.utcnow() - timedelta(minutes=6),
        date_finished=datetime.utcnow(),
        result=Result.passed,
        status=Status.finished,
    )


@pytest.fixture(scope='function')
def default_job(default_build):
    return factories.JobFactory(
        build=default_build,
        date_started=datetime.utcnow() - timedelta(minutes=6),
        date_finished=datetime.utcnow(),
        result=Result.passed,
        status=Status.finished,
    )


@pytest.fixture(scope='function')
def default_artifact(default_job):
    return factories.ArtifactFactory(
        job=default_job,
    )


@pytest.fixture(scope='function')
def default_testcase(default_job):
    return factories.TestCaseFactory(
        job=default_job,
    )


@pytest.fixture(scope='function')
def default_filecoverage(default_job):
    return factories.FileCoverageFactory(
        job=default_job,
    )


@pytest.fixture(scope='function')
def default_api_token():
    return factories.ApiTokenFactory()


@pytest.fixture(scope='function')
def default_hook_token(default_repo):
    return factories.HookTokenFactory(
        repository=default_repo,
    )


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
