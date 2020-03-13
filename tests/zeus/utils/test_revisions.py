import pytest

from zeus.exceptions import UnknownRevision
from zeus.utils.revisions import identify_revision


def test_identify_revision_database(default_repo, default_revision, mock_vcs_server):
    result = identify_revision(default_repo, ref=default_revision.sha)
    assert result == default_revision


def test_identify_revision_vcs_server(default_repo, default_revision, mock_vcs_server):
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

    result = identify_revision(default_repo, ref=default_revision.sha[:7])
    assert result == default_revision


def test_identity_revision_unknown(default_repo, default_revision, mock_vcs_server):
    mock_vcs_server.replace(
        mock_vcs_server.GET,
        "http://localhost:8070/stmt/resolve",
        status=400,
        json={"error": "invalid_ref", "ref": default_revision.sha[:7]},
    )

    with pytest.raises(UnknownRevision):
        identify_revision(default_repo, ref=default_revision.sha[:7])
