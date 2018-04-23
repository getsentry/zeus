from zeus.models import ItemStat


def test_build_details(
    client, db_session, default_login, default_repo, default_build, default_repo_access
):
    db_session.add(ItemStat(item_id=default_build.id, name="tests.count", value="1"))

    resp = client.get(
        "/api/repos/{}/builds/{}".format(
            default_repo.get_full_name(), default_build.number
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(default_build.id)
    assert data["stats"]["tests"]["count"] == 1
