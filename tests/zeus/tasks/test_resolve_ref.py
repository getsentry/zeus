from zeus import factories
from zeus.tasks import resolve_ref_for_build


def test_resolve_ref_for_build(mocker, db_session, default_revision):
    build = factories.BuildFactory.create(
        repository=default_revision.repository, ref=default_revision.sha
    )

    assert build.revision_sha is None

    resolve_ref_for_build(build.id)

    assert build.revision_sha == default_revision.sha
