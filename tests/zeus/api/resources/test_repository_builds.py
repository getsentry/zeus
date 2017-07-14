from zeus.models import Build


def test_repo_build_list(client, default_login, default_build, default_repo, default_repo_access):
    resp = client.get('/api/repos/{}/builds'.format(default_repo.name))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == str(default_build.id)


def test_repo_build_list_without_access(client, default_login, default_build, default_repo):
    resp = client.get('/api/repos/{}/builds'.format(default_repo.name))
    assert resp.status_code == 404


def test_repo_build_create(
    client, default_login, default_source, default_repo, default_repo_access
):
    resp = client.post(
        '/api/repos/{}/builds'.format(default_repo.name),
        json={
            'revision_sha': default_source.revision_sha,
            'label': 'test build',
            'author': {
                'name': 'foo',
                'email': 'foo@example.com'
            }
        }
    )
    assert resp.status_code == 200, repr(resp.data)

    build = Build.query.unrestricted_unsafe().get(resp.json()['id'])
    assert build
    assert build.repository_id == default_repo.id
    assert build.source_id == default_source.id
    assert build.label == 'test build'
    assert build.author.email == 'foo@example.com'
    assert build.author.name == 'foo'
