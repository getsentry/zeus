from io import BytesIO

from zeus import factories
from zeus.models import Artifact, PendingArtifact


def test_new_artifact(
    client, default_revision, default_repo, default_hook, sample_xunit
):
    build = factories.BuildFactory(
        revision=default_revision,
        provider=default_hook.get_provider().get_name(default_hook.config),
        external_id="3",
    )

    job = factories.JobFactory(
        build=build,
        provider=default_hook.get_provider().get_name(default_hook.config),
        external_id="2",
        in_progress=True,
    )

    path = "/hooks/{}/{}/builds/{}/jobs/{}/artifacts".format(
        default_hook.id,
        default_hook.get_signature(),
        build.external_id,
        job.external_id,
    )

    resp = client.post(
        path,
        data={
            "name": "junit.xml",
            "file": (BytesIO(sample_xunit.encode("utf-8")), "junit.xml"),
            "type": "xunit",
        },
    )

    assert resp.status_code == 201, repr(resp.data)
    data = resp.json()
    artifact = Artifact.query.get(data["id"])
    assert artifact.file.filename.endswith("junit.xml")
    assert artifact.type == "xunit"


def test_new_artifact_missing_job(
    client, default_revision, default_repo, default_hook, sample_xunit
):
    path = "/hooks/{}/{}/builds/{}/jobs/{}/artifacts".format(
        default_hook.id, default_hook.get_signature(), "3", "2"
    )

    resp = client.post(
        path,
        data={
            "name": "junit.xml",
            "file": (BytesIO(sample_xunit.encode("utf-8")), "junit.xml"),
            "type": "xunit",
        },
    )

    assert resp.status_code == 202, repr(resp.data)
    data = resp.json()
    pending_artifact = PendingArtifact.query.get(data["id"])
    assert pending_artifact.file.filename.endswith("junit.xml")
    assert pending_artifact.type == "xunit"
    assert pending_artifact.hook_id == default_hook.id
    assert pending_artifact.repository_id == default_hook.repository_id
    assert pending_artifact.external_build_id == "3"
    assert pending_artifact.external_job_id == "2"
