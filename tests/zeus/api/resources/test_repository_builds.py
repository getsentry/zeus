from zeus import factories
from zeus.models import Build
from zeus.vcs.base import UnknownRevision


def test_repo_build_list(
    client, default_login, default_revision, default_repo, default_repo_access
):
    build1 = factories.BuildFactory.create(revision=default_revision)
    build2 = factories.BuildFactory.create(revision=default_revision)

    resp = client.get(
        "/api/repos/{}/builds?show=all".format(default_repo.get_full_name())
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["id"] == str(build2.id)
    assert data[1]["id"] == str(build1.id)


def test_repo_build_list_without_access(
    client, default_login, default_build, default_repo
):
    resp = client.get("/api/repos/{}/builds".format(default_repo.get_full_name()))
    assert resp.status_code == 404


def test_repo_build_list_mine_with_match(
    client, default_login, default_build, default_repo, default_repo_access
):
    resp = client.get(
        "/api/repos/{}/builds?show=mine".format(default_repo.get_full_name())
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1


def test_repo_build_list_mine_without_match(
    client, default_login, default_repo, default_repo_access
):
    revision = factories.RevisionFactory(repository=default_repo)
    factories.BuildFactory(revision=revision)
    resp = client.get(
        "/api/repos/{}/builds?show=mine".format(default_repo.get_full_name())
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0


def test_repo_build_create(
    client, default_login, default_revision, default_repo, default_repo_access, mocker
):
    mock_identify_revision = mocker.patch("zeus.utils.revisions.identify_revision")
    mock_identify_revision.return_value = default_revision

    resp = client.post(
        "/api/repos/{}/builds".format(default_repo.get_full_name()),
        json={"ref": default_revision.sha, "label": "test build"},
    )
    assert resp.status_code == 200, repr(resp.data)

    mock_identify_revision.assert_called_once_with(
        default_repo, default_revision.sha, with_vcs=False
    )

    build = Build.query.unrestricted_unsafe().get(resp.json()["id"])
    assert build
    assert build.repository_id == default_repo.id
    assert build.ref == default_revision.sha
    assert build.revision_sha == default_revision.sha
    assert build.label == "test build"


def test_repo_build_create_missing_revision(
    client, default_login, default_revision, default_repo, default_repo_access, mocker
):
    mock_identify_revision = mocker.patch("zeus.utils.revisions.identify_revision")
    mock_identify_revision.side_effect = UnknownRevision()

    resp = client.post(
        "/api/repos/{}/builds".format(default_repo.get_full_name()),
        json={"ref": "master", "label": "test build"},
    )
    assert resp.status_code == 200, repr(resp.data)

    mock_identify_revision.assert_called_once_with(
        default_repo, "master", with_vcs=False
    )

    build = Build.query.unrestricted_unsafe().get(resp.json()["id"])
    assert build
    assert build.repository_id == default_repo.id
    assert build.ref == "master"
    assert build.revision_sha is None
    assert build.label == "test build"


def test_repo_build_existing_entityt(
    client, default_login, default_revision, default_repo, default_repo_access
):
    existing_build = factories.BuildFactory(revision=default_revision, travis=True)

    resp = client.post(
        "/api/repos/{}/builds".format(default_repo.get_full_name()),
        json={
            "provider": existing_build.provider,
            "external_id": existing_build.external_id,
            "ref": default_revision.sha,
            "label": "test build",
        },
    )
    assert resp.status_code == 422, repr(resp.data)
