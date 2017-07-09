from zeus.constants import Result


def test_job_details(
    client, default_login, default_repo, default_build, default_job, default_repo_access
):
    resp = client.get(
        '/api/repos/{}/builds/{}/jobs/{}'.
        format(default_repo.name, default_build.number, default_job.number)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == str(default_job.id)


def test_update_job(
    client, default_login, default_repo, default_build, default_job, default_repo_access
):
    assert default_job.result != Result.failed

    resp = client.put(
        '/api/repos/{}/builds/{}/jobs/{}'.format(
            default_repo.name, default_build.number, default_job.number
        ),
        json={
            'result': 'failed',
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == str(default_job.id)

    assert default_job.result == Result.failed
