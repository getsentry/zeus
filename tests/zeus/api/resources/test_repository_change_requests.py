from zeus.models import ChangeRequest


def test_create_change_request(
    client, default_login, default_repo, default_repo_access, default_source
):
    resp = client.post(
        "/api/repos/{}/change-requests".format(default_repo.get_full_name()),
        json={
            "message": "Hello world!",
            "provider": "github",
            "external_id": "123",
            "parent_revision_sha": default_source.revision_sha,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"]

    cr = ChangeRequest.query.unrestricted_unsafe().get(data["id"])
    assert cr.message == "Hello world!"
    assert cr.external_id == "123"
    assert cr.provider == "github"
