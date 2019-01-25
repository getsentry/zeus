import os
import pytest

from base64 import b64encode

from zeus import factories
from zeus.constants import Result, Status
from zeus.models import Build, ChangeRequest, Job

CONFIG_RESPONSE = b"""
{
    "config": {
        "host": "travis-ci.org",
        "shorten_host": "trvs.io",
        "assets": {
            "host": "travis-ci.org"
        },
        "pusher": {
            "key": "5df8ac576dcccf4fd076"
        },
        "github": {
            "api_url": "https://api.github.com",
            "scopes": [
                "read:org", "user:email",
                "repo_deployment", "repo:status",
                "write:repo_hook"
            ]
        },
        "notifications": {
            "webhook": {
                "public_key": "%(public_key)s"
            }
        }
    }
}
"""

UNSET = object()


@pytest.fixture(scope="session")
def sample_travis_build_commit(fixture_path):
    with open(os.path.join(fixture_path, "travis-build-commit.json"), "rb") as fp:
        return fp.read()


@pytest.fixture(scope="session")
def sample_travis_build_pr(fixture_path):
    with open(os.path.join(fixture_path, "travis-build-pull-request.json"), "rb") as fp:
        return fp.read()


def make_signature(payload, private_key) -> bytes:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding

    return private_key.sign(payload, padding.PKCS1v15(), hashes.SHA1())


def get_config_response(public_key_bytes):
    return CONFIG_RESPONSE % {b"public_key": public_key_bytes.replace(b"\n", b"\\n")}


def post_request(client, hook, payload, public_key, signature):
    path = "/hooks/{}/public/provider/travis/webhook".format(hook.id)

    return client.post(
        path, data={"payload": payload}, headers={"Signature": b64encode(signature)}
    )


def test_missing_payload(client, default_repo, default_hook):
    path = "/hooks/{}/public/provider/travis/webhook".format(default_hook.id)

    resp = client.post(path)
    assert resp.status_code == 400, repr(resp.data)


def test_missing_signature(client, default_repo, default_hook):
    path = "/hooks/{}/public/provider/travis/webhook".format(default_hook.id)

    resp = client.post(path)
    assert resp.status_code == 400, repr(resp.data)


def test_queued_build(
    client,
    default_repo,
    default_hook,
    default_revision,
    sample_travis_build_commit,
    private_key,
    public_key_bytes,
    mocker,
    responses,
):
    responses.add(
        responses.GET,
        "https://api.travis-ci.org/config",
        get_config_response(public_key_bytes),
    )

    source = factories.SourceFactory.create(revision=default_revision)

    mock_identify_revision = mocker.patch("zeus.utils.revisions.identify_revision")
    mock_identify_revision.return_value = default_revision

    resp = post_request(
        client,
        default_hook,
        sample_travis_build_commit,
        public_key_bytes,
        make_signature(sample_travis_build_commit, private_key),
    )
    assert resp.status_code == 200, repr(resp.data)

    build = (
        Build.query.unrestricted_unsafe()
        .filter(Build.provider == "api.travis-ci.org", Build.external_id == "288639281")
        .first()
    )
    assert build
    assert build.repository_id == default_repo.id
    assert build.source_id == source.id
    assert build.label == default_revision.subject
    assert (
        build.url
        == "https://travis-ci.org/travis-ci/docs-travis-ci-com/builds/288639281"
    )

    job = (
        Job.query.unrestricted_unsafe()
        .filter(Job.provider == "api.travis-ci.org", Job.external_id == "288639284")
        .first()
    )
    assert job
    assert job.build_id == build.id
    assert job.repository_id == default_repo.id
    assert job.status == Status.finished
    assert job.result == Result.passed
    assert job.allow_failure
    assert job.label == "python: 3.5.2 - TEST_SUITE=integration"
    assert (
        job.url == "https://travis-ci.org/travis-ci/docs-travis-ci-com/jobs/288639284"
    )


def test_pull_request(
    client,
    default_repo,
    default_hook,
    default_revision,
    sample_travis_build_pr,
    private_key,
    public_key_bytes,
    mocker,
    responses,
):
    responses.add(
        responses.GET,
        "https://api.travis-ci.org/config",
        get_config_response(public_key_bytes),
    )

    source = factories.SourceFactory.create(revision=default_revision)

    mock_identify_revision = mocker.patch("zeus.utils.revisions.identify_revision")
    mock_identify_revision.return_value = default_revision

    resp = post_request(
        client,
        default_hook,
        sample_travis_build_pr,
        public_key_bytes,
        make_signature(sample_travis_build_pr, private_key),
    )
    assert resp.status_code == 200, repr(resp.data)

    cr = (
        ChangeRequest.query.unrestricted_unsafe()
        .filter(ChangeRequest.provider == "github", ChangeRequest.external_id == "123")
        .first()
    )
    assert cr
    assert cr.message == "The title of the pull request"
    assert cr.parent_revision_sha == source.revision_sha
    assert cr.head_revision_sha == source.revision_sha

    build = (
        Build.query.unrestricted_unsafe()
        .filter(Build.provider == "api.travis-ci.org", Build.external_id == "288639281")
        .first()
    )
    assert build
    assert build.repository_id == default_repo.id
    assert build.source_id == source.id
    assert build.label == "PR #123 - The title of the pull request"
    assert (
        build.url
        == "https://travis-ci.org/travis-ci/docs-travis-ci-com/builds/288639281"
    )

    job = (
        Job.query.unrestricted_unsafe()
        .filter(Job.provider == "api.travis-ci.org", Job.external_id == "288639284")
        .first()
    )
    assert job
    assert job.build_id == build.id
    assert job.repository_id == default_repo.id
    assert job.status == Status.finished
    assert job.result == Result.passed
    assert job.allow_failure
    assert job.label == "python: 3.5.2 - TEST_SUITE=integration"
    assert (
        job.url == "https://travis-ci.org/travis-ci/docs-travis-ci-com/jobs/288639284"
    )
