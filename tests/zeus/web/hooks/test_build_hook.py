from zeus import factories
from zeus.models import Build


def test_new_build(client, default_source, default_repo, default_hook):
    build_xid = "2"

    path = "/hooks/{}/{}/builds/{}".format(
        default_hook.id, default_hook.get_signature(), build_xid
    )

    resp = client.post(
        path, json={"ref": default_source.revision_sha, "label": "test build"}
    )
    assert resp.status_code == 200, repr(resp.data)

    build = Build.query.unrestricted_unsafe().get(resp.json()["id"])
    assert build
    assert build.repository_id == default_repo.id
    assert build.provider == default_hook.get_provider().get_name(default_hook.config)
    assert build.external_id == build_xid
    assert build.label == "test build"


def test_existing_build(client, default_source, default_repo, default_hook):
    build = factories.BuildFactory(
        source=default_source,
        provider=default_hook.get_provider().get_name(default_hook.config),
        external_id="2",
    )

    path = "/hooks/{}/{}/builds/{}".format(
        default_hook.id, default_hook.get_signature(), build.external_id
    )

    resp = client.post(
        path, json={"ref": default_source.revision_sha, "label": "test build"}
    )
    assert resp.status_code == 200, repr(resp.data)

    build = Build.query.unrestricted_unsafe().get(build.id)
    assert build.label == "test build"
