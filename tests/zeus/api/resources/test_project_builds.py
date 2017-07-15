from zeus.models import Build


def test_project_build_list(
    client, default_login, default_org, default_project, default_build, default_repo_access
):
    resp = client.get('/api/projects/{}/{}/builds'.format(default_org.name, default_project.name))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == str(default_build.id)


def test_project_build_list_without_access(
    client, default_login, default_org, default_project, default_build
):
    resp = client.get('/api/projects/{}/{}/builds'.format(default_org.name, default_project.name))
    assert resp.status_code == 404


def test_project_build_create(
    client, default_login, default_org, default_project, default_source, default_repo_access
):
    resp = client.post(
        '/api/projects/{}/{}/builds'.format(default_org.name, default_project.name),
        json={
            'revision_sha': default_source.revision_sha,
            'label': 'test build',
        }
    )
    assert resp.status_code == 200, repr(resp.data)

    build = Build.query.unrestricted_unsafe().get(resp.json()['id'])
    assert build
    assert build.project_id == default_project.id
    assert build.source_id == default_source.id
    assert build.label == 'test build'
