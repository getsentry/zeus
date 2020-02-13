import pytest

from zeus.exceptions import UnknownRevision
from zeus.vcs.client import vcs_client


def test_log_with_unknown_revision(responses, default_repo):
    responses.add(
        responses.GET,
        f"http://localhost:8070/stmt/log?repo_id={default_repo.id}&parent=abcdef&offset=0&limit=100",
        json={"error": "invalid_ref", "ref": "abcdef"},
        status=400,
    )

    with pytest.raises(UnknownRevision) as exc:
        vcs_client.log(repo_id=default_repo.id, parent="abcdef")

        assert exc.ref == "abcdef"
