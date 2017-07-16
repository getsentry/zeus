# flake8 is breaking with no empty lines up here NOQA


def test_build_file_coverage_list(
    client, default_login, default_repo, default_build, default_filecoverage, default_repo_access
):
    resp = client.get(
        '/api/repos/{}/{}/builds/{}/file-coverage'.
        format(default_repo.owner_name, default_repo.name, default_build.number)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['filename'] == str(default_filecoverage.filename)


def test_build_file_coverage_list_filter_diff_only(
    client, default_login, default_repo, default_build, default_filecoverage, default_repo_access
):
    resp = client.get(
        '/api/repos/{}/{}/builds/{}/file-coverage?diff_only=true'.
        format(default_repo.owner_name, default_repo.name, default_build.number)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0

    resp = client.get(
        '/api/repos/{}/{}/builds/{}/file-coverage?diff_only=false'.
        format(default_repo.owner_name, default_repo.name, default_build.number)
    )
    data = resp.json()
    assert len(data) == 1
    assert data[0]['filename'] == str(default_filecoverage.filename)
