import pytest

from io import BytesIO

from zeus import factories
from zeus.models import Artifact


@pytest.mark.xfail
def test_new_artifact(client, default_source, default_repo, default_hook, sample_xunit):
    build = factories.BuildFactory(
        source=default_source,
        provider=default_hook.provider,
        external_id='3',
    )

    job = factories.JobFactory(
        build=build,
        provider=default_hook.provider,
        external_id='2',
        in_progress=True,
    )

    path = '/hooks/{}/{}/builds/{}/jobs/{}/artifacts'.format(
        default_hook.id, default_hook.get_signature(), build.external_id, job.external_id
    )

    resp = client.post(
        path,
        data={
            'name': 'junit.xml',
            'file': (BytesIO(sample_xunit.encode('utf-8')), 'junit.xml'),
        },
    )

    assert resp.status_code == 201, repr(resp.data)
    data = resp.json()
    artifact = Artifact.query.get(data['id'])
    assert artifact.file.filename.endswith('junit.xml')
