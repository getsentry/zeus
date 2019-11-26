from flask import current_app

from zeus import factories


def test_time_aggregate(
    client, default_login, default_repo, default_repo_access, default_revision
):
    factories.BuildFactory(revision=default_revision, passed=True)

    resp = client.get(
        "/api/repos/{}/stats?aggregate=time&points=30&resolution=1d&stat=builds.total".format(
            default_repo.get_full_name()
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 30
    for item in data[1:]:
        assert item["stats"]["builds.total"] == 0
    assert data[0]["stats"]["builds.total"] == 1


def test_build_aggregate(
    client, default_login, default_repo, default_repo_access, default_revision
):
    build = factories.BuildFactory(revision=default_revision, passed=True)

    current_app.config["MOCK_REVISIONS"] = True
    try:
        resp = client.get(
            "/api/repos/{}/stats?aggregate=build&points=30&stat=builds.total".format(
                default_repo.get_full_name()
            )
        )
    finally:
        current_app.config["MOCK_REVISIONS"] = False

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0] == {"build": build.number, "stats": {"builds.total": 1}}
