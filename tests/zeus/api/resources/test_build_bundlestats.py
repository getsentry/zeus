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

    entrypoint1 = factories.BundleEntrypointFactory.create(
        job=job1,
        name='bar',
    )
    asset1 = factories.BundleAssetFactory.create(
        job=job1,
        name='foo',
        size=50,
    )
    entrypoint1.assets.append(asset1)

    entrypoint2 = factories.BundleEntrypointFactory.create(
        job=job2,
        name='foo',
    )
    entrypoint3 = factories.BundleEntrypointFactory.create(
        job=job2,
        name='bar',
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
    assert sorted(data[0]['results'], key=lambda x: x['assets']) == [{
        'id': str(entrypoint3.id),
        'job_id': str(job2.id),
        'assets': [],
    }, {
        'id': str(entrypoint1.id),
        'job_id': str(job1.id),
        'assets': [{
            'name': 'foo',
            'size': 50,
        }],
    }]
    assert data[1]['name'] == 'foo'
    assert data[1]['results'] == [{
        'id': str(entrypoint2.id),
        'job_id': str(job2.id),
        'assets': [],
    }]
