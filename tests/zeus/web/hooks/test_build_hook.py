from zeus import factories
from zeus.models import Build


def test_new_build(client, default_source, default_repo, default_hook):
    build_xid = '2'

    path = '/hooks/{}/{}/builds/{}'.format(default_hook.id, default_hook.get_signature(), build_xid)

    resp = client.post(
        path, json={
            'revision_sha': default_source.revision_sha,
            'label': 'test build',
        }
    )
    assert resp.status_code == 200, repr(resp.data)

    build = Build.query.unrestricted_unsafe().get(resp.json()['id'])
    assert build
    assert build.repository_id == default_repo.id
    assert build.provider == default_hook.provider
    assert build.external_id == build_xid


def test_existing_build(client, default_source, default_repo, default_hook):
    build = factories.BuildFactory(
        source=default_source,
        provider=default_hook.provider,
        external_id='2',
    )

    path = '/hooks/{}/{}/builds/{}'.format(
        default_hook.id, default_hook.get_signature(), build.external_id
    )

    resp = client.post(
        path, json={
            'revision_sha': default_source.revision_sha,
            'label': 'test build',
        }
    )
    assert resp.status_code == 200, repr(resp.data)
