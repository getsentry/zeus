import json
import os
import pytest

from time import time

from zeus.constants import Result, Status
from zeus.models import Build, ChangeRequest, Job
from zeus.tasks import process_travis_webhook


@pytest.fixture(scope="session")
def sample_travis_build_commit(fixture_path):
    with open(os.path.join(fixture_path, "travis-build-commit.json"), "rb") as fp:
        return json.load(fp)


@pytest.fixture(scope="session")
def sample_travis_build_pr(fixture_path):
    with open(os.path.join(fixture_path, "travis-build-pull-request.json"), "rb") as fp:
        return json.load(fp)


def test_commit(
    default_hook, default_repo, default_revision, sample_travis_build_commit, mocker
):
    mock_identify_revision = mocker.patch("zeus.utils.revisions.identify_revision")
    mock_identify_revision.return_value = default_revision

    process_travis_webhook(
        hook_id=default_hook.id,
        payload=sample_travis_build_commit,
        timestamp_ms=int(time() * 1000),
    )

    build = (
        Build.query.unrestricted_unsafe()
        .filter(Build.provider == "api.travis-ci.org", Build.external_id == "288639281")
        .first()
    )
    assert build
    assert build.repository_id == default_repo.id
    assert build.revision_sha == default_revision.sha
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


def test_pull_request(default_repo, default_hook, sample_travis_build_pr):
    process_travis_webhook(
        hook_id=default_hook.id,
        payload=sample_travis_build_pr,
        timestamp_ms=int(time() * 1000),
    )

    cr = (
        ChangeRequest.query.unrestricted_unsafe()
        .filter(ChangeRequest.provider == "github", ChangeRequest.external_id == "123")
        .first()
    )
    assert cr
    assert cr.message == "The title of the pull request"
    assert cr.parent_ref == "d79e3a6ff0cada29d731ed93de203f76a81d02c0"
    assert cr.parent_revision_sha is None
    assert cr.head_ref == "d79e3a6ff0cada29d731ed93de203f76a81d02c0"
    assert cr.head_revision_sha is None
    assert cr.author is None

    build = (
        Build.query.unrestricted_unsafe()
        .filter(Build.provider == "api.travis-ci.org", Build.external_id == "288639281")
        .first()
    )
    assert build
    assert build.repository_id == default_repo.id
    assert build.ref == cr.parent_ref
    assert build.revision_sha == cr.parent_revision_sha
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
