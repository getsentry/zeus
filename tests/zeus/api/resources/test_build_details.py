# NOQA


def test_build_details(
    client, default_login, default_org, default_project, default_build, default_repo_access
):
    resp = client.get(
        '/api/projects/{}/{}/builds/{}'.
        format(default_org.name, default_project.name, default_build.number)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == str(default_build.id)


def test_build_update(
    client, default_login, default_org, default_project, default_build, default_repo_access
):
    resp = client.put(
        '/api/projects/{}/{}/builds/{}'.format(
            default_org.name, default_project.name, default_build.number
        ),
        json={
            'label': 'foobar',
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == str(default_build.id)
    assert default_build.label == 'foobar'
