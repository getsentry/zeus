from zeus import factories
from zeus.constants import Severity


def test_build_styleviolations_list(
    client, db_session, default_login, default_repo, default_build, default_repo_access
):
    job1 = factories.JobFactory(
        build=default_build,
    )
    job2 = factories.JobFactory(
        build=default_build,
    )
    db_session.add(job1)
    db_session.add(job2)

    violation1 = factories.StyleViolationFactory(
        job=job1,
        filename='bar',
    )
    violation2 = factories.StyleViolationFactory(
        job=job2,
        filename='foo',
    )
    db_session.add(violation1)
    db_session.add(violation2)

    resp = client.get(
        '/api/repos/{}/builds/{}/style-violations'.
        format(default_repo.get_full_name(), default_build.number)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]['id'] == str(violation1.id)
    assert data[1]['id'] == str(violation2.id)


def test_build_styleviolations_list_empty(
    client, default_login, default_repo, default_build, default_repo_access
):
    resp = client.get(
        '/api/repos/{}/builds/{}/style-violations'.
        format(default_repo.get_full_name(), default_build.number)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0


def test_build_styleviolations_list_severity_filter(
    client, default_login, default_repo, default_build, default_job, default_repo_access
):
    violation = factories.StyleViolationFactory(
        job=default_job,
        severity=Severity.error
    )

    resp = client.get(
        '/api/repos/{}/builds/{}/style-violations?severity=warning'.
        format(default_repo.get_full_name(), default_build.number)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0

    resp = client.get(
        '/api/repos/{}/builds/{}/style-violations?severity=error'.
        format(default_repo.get_full_name(), default_build.number)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == str(violation.id)
