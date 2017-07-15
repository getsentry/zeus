import os
import pytest

from datetime import datetime, timedelta, timezone

from zeus import factories, models

DATA_FIXTURES = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'tests', 'fixtures')


@pytest.fixture(scope='function')
def default_user():
    return factories.UserFactory(
        email='foo@example.com',
    )


@pytest.fixture(scope='function')
def default_identity(default_user):
    return factories.IdentityFactory(
        user=default_user,
        github=True,
    )


@pytest.fixture(scope='function')
def default_login(client, default_user):
    with client.session_transaction() as session:
        session['uid'] = default_user.id.hex

    yield default_user


@pytest.fixture(scope='function')
def default_org():
    return factories.OrganizationFactory(name='getsentry')


@pytest.fixture(scope='function')
def default_org_access(db_session, default_org, default_user):
    access = models.OrganizationAccess(
        organization_id=default_org.id,
        user_id=default_user.id,
    )
    db_session.add(access)
    db_session.commit()

    return access


@pytest.fixture(scope='function')
def default_project(default_repo):
    return factories.ProjectFactory(
        repository=default_repo,
        name='zeus',
    )


@pytest.fixture(scope='function')
def default_repo(default_org):
    return factories.RepositoryFactory(
        organization=default_org,
        url='https://github.com/getsentry/zeus.git',
        backend=models.RepositoryBackend.git,
        status=models.RepositoryStatus.active,
    )


@pytest.fixture(scope='function')
def default_repo_access(db_session, default_repo, default_org_access, default_user):
    access = models.RepositoryAccess(
        organization_id=default_repo.organization_id,
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
def default_parent_revision(default_repo, default_revision):
    return factories.RevisionFactory(
        repository=default_repo,
        parents=[default_revision.sha],
        sha='adba8d362c656c7f97f5da9fa4e644be1b72a449',
    )


@pytest.fixture(scope='function')
def default_source(default_revision, default_patch):
    return factories.SourceFactory(
        revision=default_revision,
        patch=default_patch,
    )


@pytest.fixture(scope='function')
def default_patch(default_parent_revision):
    return factories.PatchFactory(
        parent_revision=default_parent_revision,
    )


@pytest.fixture(scope='function')
def default_build(default_source, default_project):
    return factories.BuildFactory(
        source=default_source,
        project=default_project,
        date_started=datetime.now(timezone.utc) - timedelta(minutes=6),
        date_finished=datetime.now(timezone.utc),
        passed=True,
    )


@pytest.fixture(scope='function')
def default_job(default_build):
    return factories.JobFactory(
        build=default_build,
        date_started=datetime.now(timezone.utc) - timedelta(minutes=6),
        date_finished=datetime.now(timezone.utc),
        passed=True,
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
        passed=True,
    )


@pytest.fixture(scope='function')
def default_filecoverage(default_job):
    return factories.FileCoverageFactory(
        job=default_job,
    )


@pytest.fixture(scope='function')
def default_hook(default_project):
    return factories.HookFactory(
        project=default_project,
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


@pytest.fixture(scope='session')
def sample_diff():
    with open(os.path.join(DATA_FIXTURES, 'sample.diff')) as fp:
        return fp.read()
