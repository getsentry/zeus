from zeus import factories


def test_simple(
    client, db_session, default_login, default_repo, default_repo_access, default_revision
):
    source = factories.SourceFactory(
        revision=default_revision,
    )

    # finished build
    build = factories.BuildFactory(
        source=source,
        passed=True,
    )
    db_session.add(build)

    # an unfinished build which shouldn't be used
    factories.BuildFactory(
        source=source,
    )
    db_session.add(build)

    coverage1 = factories.FileCoverageFactory(
        build=build,
        filename='foo/bar.py',
        lines_covered=50,
        lines_uncovered=100,
    )
    db_session.add(coverage1)
    coverage2 = factories.FileCoverageFactory(
        build=build,
        filename='foo/baz.py',
        lines_covered=20,
        lines_uncovered=20,
    )
    db_session.add(coverage2)
    coverage3 = factories.FileCoverageFactory(
        build=build,
        filename='blah/blah.py',
        lines_covered=5,
        lines_uncovered=0,
    )
    db_session.add(coverage3)

    db_session.commit()

    path = '/api/repos/{}/builds/{}/file-coverage-tree'.format(
        default_repo.get_full_name(),
        build.number,
    )

    resp = client.get(path)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data['entries']) == 2
    assert data['entries'][0]['name'] == 'blah/blah.py'
    assert data['entries'][0]['path'] == 'blah/blah.py'
    assert data['entries'][0]['lines_covered'] == 5
    assert data['entries'][0]['lines_uncovered'] == 0
    assert data['entries'][1]['name'] == 'foo'
    assert data['entries'][1]['path'] == 'foo'
    assert data['entries'][1]['lines_covered'] == 70
    assert data['entries'][1]['lines_uncovered'] == 120
    assert len(data['trail']) == 0

    resp = client.get('{}?parent=foo'.format(path))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data['entries']) == 2
    assert data['entries'][0]['name'] == 'bar.py'
    assert data['entries'][0]['path'] == 'foo/bar.py'
    assert data['entries'][0]['lines_covered'] == 50
    assert data['entries'][0]['lines_uncovered'] == 100
    assert data['entries'][1]['name'] == 'baz.py'
    assert data['entries'][1]['path'] == 'foo/baz.py'
    assert data['entries'][1]['lines_covered'] == 20
    assert data['entries'][1]['lines_uncovered'] == 20
    assert len(data['trail']) == 1
    assert data['trail'][0] == {
        'name': 'foo',
        'path': 'foo',
    }
