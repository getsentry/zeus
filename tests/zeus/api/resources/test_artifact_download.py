def test_artifact_download(
    client,
    default_login,
    default_repo,
    default_build,
    default_job,
    default_artifact,
    default_repo_access,
):
    resp = client.get(
        "/api/repos/{}/builds/{}/jobs/{}/artifacts/{}/download".format(
            default_repo.get_full_name(),
            default_build.number,
            default_job.number,
            default_artifact.id,
        )
    )
    assert resp.status_code == 302
    assert resp.headers["Location"] == "https://example.com/artifacts/junit.xml"
