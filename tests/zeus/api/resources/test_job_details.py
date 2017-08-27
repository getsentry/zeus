from zeus.constants import Result, Status


def test_job_details(
    client, default_login, default_repo, default_build, default_job, default_repo_access
):
    resp = client.get(
        '/api/repos/{}/builds/{}/jobs/{}'.format(
            default_repo.get_full_name(), default_build.number, default_job.number
        )
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == str(default_job.id)


def test_update_job_to_finished(
    client, mocker, default_login, default_repo, default_build, default_job, default_repo_access
):
    assert default_job.result != Result.failed

    mock_delay = mocker.patch('zeus.tasks.aggregate_build_stats_for_job.delay')

    resp = client.put(
        '/api/repos/{}/builds/{}/jobs/{}'.format(
            default_repo.get_full_name(), default_build.number, default_job.number
        ),
        json={
            'result': 'failed',
            'status': 'finished',
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == str(default_job.id)

    assert default_job.status == Status.finished
    assert default_job.result == Result.failed

    mock_delay.assert_called_once_with(job_id=default_job.id)


def test_update_job_to_in_progress(
    client, mocker, default_login, default_repo, default_build, default_job, default_repo_access
):
    assert default_job.result != Result.failed

    mock_delay = mocker.patch('zeus.tasks.aggregate_build_stats_for_job.delay')

    resp = client.put(
        '/api/repos/{}/builds/{}/jobs/{}'.format(
            default_repo.get_full_name(), default_build.number, default_job.number
        ),
        json={
            'status': 'in_progress',
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == str(default_job.id)

    assert default_job.status == Status.in_progress

    mock_delay.assert_called_once_with(job_id=default_job.id)
