from zeus import factories
from zeus.constants import Result, Status


def test_simple(
    client, db_session, default_login, default_repo, default_repo_access, default_source,
    default_build
):

    # an unfinished build which shouldn't be used
    build = factories.BuildFactory(
        repository=default_repo,
        source=default_source,
        status=Status.in_progress,
    )
    db_session.add(build)

    # a couple of needed jobs that split the tests
    job1 = factories.JobFactory(
        repository=default_repo,
        build=default_build,
        status=Status.finished,
        result=Result.passed,
    )
    db_session.add(job1)
    job2 = factories.JobFactory(
        repository=default_repo,
        build=default_build,
        status=Status.finished,
        result=Result.passed,
    )
    db_session.add(job2)

    # and finally our testcases
    test1 = factories.TestCaseFactory(
        repository=default_repo,
        job=job1,
        name='foo.bar',
        duration=50,
    )
    db_session.add(test1)
    test2 = factories.TestCaseFactory(
        repository=default_repo,
        job=job1,
        name='foo.baz',
        duration=70,
    )
    db_session.add(test2)
    test3 = factories.TestCaseFactory(
        repository=default_repo,
        job=job2,
        name='blah.blah',
        duration=10,
    )
    db_session.add(test3)

    db_session.commit()

    path = '/api/repos/{}/test-tree'.format(default_repo.name)

    resp = client.get(path)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data['groups']) == 2
    assert data['groups'][0]['name'] == 'foo'
    assert data['groups'][0]['path'] == 'foo'
    assert data['groups'][0]['numTests'] == 2
    assert data['groups'][0]['totalDuration'] == 120
    assert data['groups'][1]['name'] == 'blah.blah'
    assert data['groups'][1]['path'] == 'blah.blah'
    assert data['groups'][1]['numTests'] == 1
    assert data['groups'][1]['totalDuration'] == 10
    assert len(data['trail']) == 0

    resp = client.get('{}?parent=foo'.format(path))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data['groups']) == 2
    assert data['groups'][0]['name'] == 'baz'
    assert data['groups'][0]['path'] == 'foo.baz'
    assert data['groups'][0]['numTests'] == 1
    assert data['groups'][0]['totalDuration'] == 70
    assert data['groups'][1]['name'] == 'bar'
    assert data['groups'][1]['path'] == 'foo.bar'
    assert data['groups'][1]['numTests'] == 1
    assert data['groups'][1]['totalDuration'] == 50
    assert len(data['trail']) == 1
    assert data['trail'][0] == {
        'name': 'foo',
        'path': 'foo',
    }
