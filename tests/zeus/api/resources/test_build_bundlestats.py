from zeus import factories


def test_build_bundle_stats(
    client, db_session, default_login, default_repo, default_build, default_repo_access
):
    job1 = factories.JobFactory.create(
        build=default_build,
    )
    job2 = factories.JobFactory.create(
        build=default_build,
    )

    bundle1 = factories.BundleFactory.create(
        job=job1,
        name='bar',
    )
    factories.BundleAssetFactory.create(
        job=job1,
        bundle=bundle1,
        name='foo',
        size=50,
    )

    factories.BundleFactory.create(
        job=job2,
        name='foo',
    )
    db_session.flush()

    resp = client.get(
        '/api/repos/{}/builds/{}/bundle-stats'.
        format(default_repo.get_full_name(), default_build.number)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]['name'] == 'bar'
    assert data[0]['assets'] == [{
        'name': 'foo',
        'size': 50,
    }]
    assert data[1]['name'] == 'foo'
    assert data[1]['assets'] == []
