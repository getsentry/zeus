from zeus import factories
from zeus.tasks import resolve_ref_for_build, resolve_ref_for_change_request


def test_resolve_ref_for_build(default_revision, mock_vcs_server):
    mock_vcs_server.replace(
        mock_vcs_server.GET,
        "http://localhost:8070/stmt/log",
        json={
            "log": [
                {
                    "sha": default_revision.sha,
                    "message": default_revision.message,
                    "authors": [
                        (default_revision.author.name, default_revision.author.email)
                    ],
                }
            ]
        },
    )

    build = factories.BuildFactory.create(
        repository=default_revision.repository,
        ref=default_revision.sha,
        author=None,
        label=None,
    )

    assert build.revision_sha is None
    assert build.author_id is None
    assert build.label is None

    resolve_ref_for_build(build.id)

    assert build.revision_sha == default_revision.sha
    assert build.author_id == default_revision.author_id
    assert build.label == "ref: Remove outdated comment"


def test_resolve_ref_for_change_request_parent_only(default_revision, mock_vcs_server):
    mock_vcs_server.replace(
        mock_vcs_server.GET,
        "http://localhost:8070/stmt/log",
        json={
            "log": [
                {
                    "sha": default_revision.sha,
                    "message": default_revision.message,
                    "authors": [
                        (default_revision.author.name, default_revision.author.email)
                    ],
                }
            ]
        },
    )

    cr = factories.ChangeRequestFactory.create(
        repository=default_revision.repository,
        parent_ref=default_revision.sha,
        head_ref=None,
        author=None,
    )

    assert cr.parent_revision_sha is None
    assert cr.head_revision_sha is None
    assert cr.author_id is None

    resolve_ref_for_change_request(cr.id)

    assert cr.parent_revision_sha == default_revision.sha
    assert cr.head_revision_sha is None
    assert cr.author_id == default_revision.author_id


def test_resolve_ref_for_change_request_parent_and_head(
    default_revision, mock_vcs_server
):
    mock_vcs_server.replace(
        mock_vcs_server.GET,
        "http://localhost:8070/stmt/log",
        json={
            "log": [
                {
                    "sha": default_revision.sha,
                    "message": default_revision.message,
                    "authors": [
                        (default_revision.author.name, default_revision.author.email)
                    ],
                }
            ]
        },
    )

    cr = factories.ChangeRequestFactory.create(
        repository=default_revision.repository,
        parent_ref=default_revision.sha,
        head_ref=default_revision.sha,
        author=None,
    )

    assert cr.parent_revision_sha is None
    assert cr.head_revision_sha is None
    assert cr.author_id is None

    resolve_ref_for_change_request(cr.id)

    assert cr.parent_revision_sha == default_revision.sha
    assert cr.head_revision_sha == default_revision.sha
    assert cr.author_id == default_revision.author_id
