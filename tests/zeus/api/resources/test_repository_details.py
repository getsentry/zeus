from zeus.models import Repository, RepositoryStatus


def test_repo_details(client, default_login, default_repo, default_repo_access):
    resp = client.get("/api/repos/{}".format(default_repo.get_full_name()))
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(default_repo.id)
    assert data["permissions"]["admin"]
    assert data["permissions"]["read"]
    assert data["permissions"]["write"]


def test_update_cannot_change_provider(
    client, default_login, default_repo, default_repo_access
):
    resp = client.put(
        "/api/repos/{}".format(default_repo.get_full_name()), json={"provider": "git"}
    )
    assert resp.status_code == 403
    repo = Repository.query.unrestricted_unsafe().get(default_repo.id)
    assert repo.provider.name == "github"


def test_update_change_public(client, default_login, default_repo, default_repo_access):
    resp = client.put(
        "/api/repos/{}".format(default_repo.get_full_name()), json={"public": True}
    )
    assert resp.status_code == 200
    repo = Repository.query.unrestricted_unsafe().get(default_repo.id)
    assert repo.public

    resp = client.put(
        "/api/repos/{}".format(default_repo.get_full_name()), json={"public": False}
    )
    assert resp.status_code == 200
    repo = Repository.query.unrestricted_unsafe().get(default_repo.id)
    assert not repo.public


def test_cannot_update_without_admin(
    client, default_login, default_repo, default_repo_write_access
):
    resp = client.put(
        "/api/repos/{}".format(default_repo.get_full_name()), json={"public": True}
    )
    assert resp.status_code == 400


def test_delete_repository(
    client, mocker, default_login, default_repo, default_repo_access
):
    mock_delay = mocker.patch("zeus.config.celery.delay")

    resp = client.delete("/api/repos/{}".format(default_repo.get_full_name()))

    assert resp.status_code == 202
    mock_delay.assert_called_once_with(
        "zeus.delete_repo", repository_id=default_repo.id
    )

    default_repo = Repository.query.get(default_repo.id)
    assert default_repo.status == RepositoryStatus.inactive


def test_delete_non_existing_repository(client, default_login):
    resp = client.delete("/api/repos/gh/getsentry/does-not-exist")

    assert resp.status_code == 404


def test_delete_inactive_repository(
    client, db_session, mocker, default_login, default_repo, default_repo_access
):
    default_repo.status = RepositoryStatus.inactive
    db_session.add(default_repo)
    db_session.flush()

    mock_delay = mocker.patch("zeus.config.celery.delay")

    resp = client.delete("/api/repos/{}".format(default_repo.get_full_name()))

    assert resp.status_code == 202
    assert not mock_delay.mock_calls
