from zeus import factories
from zeus.models import FailureReason
from zeus.tasks import resolve_ref_for_build, resolve_ref_for_change_request


def test_resolve_ref_for_build(default_revision, mock_vcs_server):
    mock_vcs_server.replace(
        mock_vcs_server.GET,
        "http://localhost:8070/stmt/resolve",
        json={
            "resolve": {
                "sha": default_revision.sha,
                "message": default_revision.message,
                "authors": [
                    (
                        default_revision.authors[0].name,
                        default_revision.authors[0].email,
                    )
                ],
            }
        },
    )

    build = factories.BuildFactory.create(
        repository=default_revision.repository,
        ref=default_revision.sha,
        label=None,
        authors=[],
    )

    assert build.revision_sha is None
    assert build.label is None
    assert not build.authors

    resolve_ref_for_build(build.id)

    assert build.revision_sha == default_revision.sha
    assert build.label == "ref: Remove outdated comment"
    assert build.authors == default_revision.authors


def test_resolve_ref_for_change_request_parent_only(default_revision, mock_vcs_server):
    mock_vcs_server.replace(
        mock_vcs_server.GET,
        "http://localhost:8070/stmt/resolve",
        json={
            "resolve": {
                "sha": default_revision.sha,
                "message": default_revision.message,
                "authors": [
                    (
                        default_revision.authors[0].name,
                        default_revision.authors[0].email,
                    )
                ],
            }
        },
    )

    cr = factories.ChangeRequestFactory.create(
        repository=default_revision.repository,
        parent_ref=default_revision.sha,
        head_ref=None,
        authors=[],
    )

    assert cr.parent_revision_sha is None
    assert cr.head_revision_sha is None
    assert not cr.authors

    resolve_ref_for_change_request(cr.id)

    assert cr.parent_revision_sha == default_revision.sha
    assert cr.head_revision_sha is None
    assert not cr.authors


def test_resolve_ref_for_change_request_head_only(default_revision, mock_vcs_server):
    mock_vcs_server.replace(
        mock_vcs_server.GET,
        "http://localhost:8070/stmt/resolve",
        json={
            "resolve": {
                "sha": default_revision.sha,
                "message": default_revision.message,
                "authors": [
                    (
                        default_revision.authors[0].name,
                        default_revision.authors[0].email,
                    )
                ],
            }
        },
    )

    cr = factories.ChangeRequestFactory.create(
        repository=default_revision.repository,
        head_ref=default_revision.sha,
        parent_ref=None,
        authors=[],
    )

    assert cr.parent_revision_sha is None
    assert cr.head_revision_sha is None
    assert not cr.authors

    resolve_ref_for_change_request(cr.id)

    assert cr.parent_revision_sha is None
    assert cr.head_revision_sha == default_revision.sha
    assert cr.authors == default_revision.authors


def test_resolve_ref_for_change_request_parent_and_head(
    default_revision, mock_vcs_server
):
    mock_vcs_server.replace(
        mock_vcs_server.GET,
        "http://localhost:8070/stmt/resolve",
        json={
            "resolve": {
                "sha": default_revision.sha,
                "message": default_revision.message,
                "authors": [
                    (
                        default_revision.authors[0].name,
                        default_revision.authors[0].email,
                    )
                ],
            }
        },
    )

    cr = factories.ChangeRequestFactory.create(
        repository=default_revision.repository,
        parent_ref=default_revision.sha,
        head_ref=default_revision.sha,
        authors=[],
    )

    assert cr.parent_revision_sha is None
    assert cr.head_revision_sha is None

    resolve_ref_for_change_request(cr.id)

    assert cr.parent_revision_sha == default_revision.sha
    assert cr.head_revision_sha == default_revision.sha
    assert cr.authors == default_revision.authors


def test_resolve_ref_unresolvable(default_repo, mock_vcs_server):
    mock_vcs_server.replace(
        mock_vcs_server.GET,
        "http://localhost:8070/stmt/resolve",
        status=400,
        json={"error": "invalid_ref", "ref": "abcdef"},
    )

    build = factories.BuildFactory.create(
        repository=default_repo, ref="abcdef", authors=[], label=None
    )

    assert build.revision_sha is None
    assert build.label is None
    assert not build.authors

    resolve_ref_for_build(build.id)

    assert build.revision_sha is None
    assert build.label is None
    assert not build.authors

    reasons = list(FailureReason.query.filter(FailureReason.build_id == build.id))
    assert len(reasons) == 1
    assert reasons[0].reason == FailureReason.Reason.unresolvable_ref
    assert reasons[0].job_id is None
