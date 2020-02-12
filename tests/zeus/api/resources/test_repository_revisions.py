from datetime import timedelta

from zeus import factories
from zeus.utils import timezone


def test_repo_revision_list(
    client,
    db_session,
    default_login,
    default_revision,
    default_repo,
    default_repo_access,
    default_user,
    mock_vcs_server,
):

    mock_vcs_server.replace(
        mock_vcs_server.GET,
        "http://localhost:8070/stmt/log",
        json={"log": [{"sha": default_revision.sha}]},
    )

    factories.BuildFactory.create(
        revision=default_revision, date_created=timezone.now() - timedelta(minutes=1)
    )
    factories.BuildFactory.create(revision=default_revision, passed=True)

    resp = client.get("/api/repos/{}/revisions".format(default_repo.get_full_name()))

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["sha"] == default_revision.sha
    assert data[0]["latest_build"]["status"] == "finished"
