from base64 import b64encode
from io import BytesIO

from zeus.models import Artifact


def test_job_artifacts_list(
    client,
    default_login,
    default_repo,
    default_build,
    default_job,
    default_artifact,
    default_repo_access,
):
    resp = client.get(
        "/api/repos/{}/builds/{}/jobs/{}/artifacts".format(
            default_repo.get_full_name(), default_build.number, default_job.number
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == str(default_artifact.id)


def test_job_artifacts_list_empty(
    client, default_login, default_repo, default_build, default_job, default_repo_access
):
    resp = client.get(
        "/api/repos/{}/builds/{}/jobs/{}/artifacts".format(
            default_repo.get_full_name(), default_build.number, default_job.number
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0


def test_create_job_artifact(
    client,
    default_login,
    default_repo,
    default_build,
    default_job,
    default_repo_access,
    sample_xunit,
):
    resp = client.post(
        "/api/repos/{}/builds/{}/jobs/{}/artifacts".format(
            default_repo.get_full_name(), default_build.number, default_job.number
        ),
        data={
            "name": "junit.xml",
            "file": (BytesIO(sample_xunit.encode("utf-8")), "junit.xml"),
            "type": "xunit",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    artifact = Artifact.query.get(data["id"])
    assert artifact.file.filename.endswith("junit.xml")
    assert artifact.type == "xunit"
    assert artifact.date_updated


def test_create_job_artifact_as_base64(
    client,
    default_login,
    default_repo,
    default_build,
    default_job,
    default_repo_access,
    sample_xunit,
):
    resp = client.post(
        "/api/repos/{}/builds/{}/jobs/{}/artifacts".format(
            default_repo.get_full_name(), default_build.number, default_job.number
        ),
        json={
            "name": "junit.xml",
            "file": b64encode(sample_xunit.encode("utf-8")).decode("utf-8"),
            "type": "xunit",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    artifact = Artifact.query.get(data["id"])
    assert artifact.file.filename.endswith("junit.xml")
    assert artifact.type == "xunit"
