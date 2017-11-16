import os
import pytest

from collections import namedtuple
from datetime import datetime, timedelta
from subprocess import check_call, check_output

from zeus import factories, models
from zeus.utils import timezone

DATA_FIXTURES = os.path.join(os.path.dirname(
    __file__), os.pardir, os.pardir, 'tests', 'fixtures')

RepoConfig = namedtuple(
    'RepoConfig', ['url', 'path', 'remote_path', 'commits'])


@pytest.fixture(scope='function')
def default_user():
    user = factories.UserFactory(
        email='foo@example.com',
    )
    factories.EmailFactory(
        user=user,
        email=user.email,
        verified=True,
    )
    return user


@pytest.fixture(scope='function')
def default_identity(default_user):
    return factories.IdentityFactory(
        user=default_user,
        github=True,
    )


@pytest.fixture(scope='function')
def default_login(client, default_user):
    with client.session_transaction() as session:
        # XXX(dcramer): could use auth.login_user here, but that makes most tests dependent
        # on that one function
        session['uid'] = default_user.id
        session['expire'] = int(
            (timezone.now() + timedelta(days=1)).strftime('%s'))

    yield default_user


@pytest.fixture(scope='function')
def default_repo():
    return factories.RepositoryFactory(
        owner_name='getsentry',
        name='zeus',
        url='https://github.com/getsentry/zeus.git',
        backend=models.RepositoryBackend.git,
        status=models.RepositoryStatus.active,
        provider=models.RepositoryProvider.github,
        github=True,
        external_id='1',
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
def default_author(default_repo, default_user):
    return factories.AuthorFactory(
        repository=default_repo,
        name='Fizz Buzz',
        email=default_user.email,
    )


@pytest.fixture(scope='function')
def default_revision(default_repo, default_author):
    return factories.RevisionFactory(
        repository=default_repo,
        author=default_author,
        sha='884ea9e17b53933febafd7e02d8bd28f3c9d479d',
    )


@pytest.fixture(scope='function')
def default_parent_revision(default_author, default_repo, default_revision):
    return factories.RevisionFactory(
        author=default_author,
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
def default_build(default_source):
    return factories.BuildFactory(
        source=default_source,
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
def default_filecoverage(default_build):
    return factories.FileCoverageFactory(
        build=default_build,
        lines_covered=30,
        lines_uncovered=60,
        diff_lines_covered=0,
        diff_lines_uncovered=0,
    )


@pytest.fixture(scope='function')
def default_api_token():
    return factories.ApiTokenFactory()


@pytest.fixture(scope='function')
def default_hook(default_repo):
    return factories.HookFactory(
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


@pytest.fixture(scope='session')
def sample_diff():
    with open(os.path.join(DATA_FIXTURES, 'sample.diff')) as fp:
        return fp.read()


@pytest.fixture(scope='session')
def sample_checkstyle():
    with open(os.path.join(DATA_FIXTURES, 'sample-checkstyle.xml')) as fp:
        return fp.read()


@pytest.fixture(scope='function')
def git_repo_config():
    root = '/tmp/zeus-git-test'
    path = '%s/clone' % (root, )
    remote_path = '%s/remote' % (root, )
    url = 'file://%s' % (remote_path, )

    check_call('rm -rf %s' % (root, ), shell=True)
    check_call('mkdir -p %s %s' % (path, remote_path), shell=True)
    check_call('git init %s' % (remote_path, ), shell=True)
    check_call(
        'cd {0} && git config --replace-all "user.name" "{1}"'.format(
            remote_path, 'Foo Bar'),
        shell=True
    )
    check_call(
        'cd {0} && git config --replace-all "user.email" "{1}"'.format(
            remote_path, 'foo@example.com'),
        shell=True
    )
    check_call(
        'cd %s && touch FOO && git add FOO && git commit -m "test\nlol\n"' % (
            remote_path, ),
        shell=True
    )
    check_call(
        'cd %s && touch BAR && git add BAR && git commit -m "biz\nbaz\n"' % (
            remote_path, ),
        shell=True
    )
    commits = check_output(
        'cd %s && git log --format=%%H --max-count=2' % (remote_path, ),
        shell=True
    ).decode('utf-8').split('\n')

    yield RepoConfig(url, path, remote_path, commits)

    check_call('rm -rf %s' % (root, ), shell=True)
