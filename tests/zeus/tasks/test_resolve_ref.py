from zeus import factories
from zeus.tasks import resolve_ref_for_build, resolve_ref_for_change_request


def test_resolve_ref_for_build(default_revision):
    build = factories.BuildFactory.create(
        repository=default_revision.repository, ref=default_revision.sha
    )

    assert build.revision_sha is None

    resolve_ref_for_build(build.id)

    assert build.revision_sha == default_revision.sha


def test_resolve_ref_for_change_request_parent_only(default_revision):
    cr = factories.ChangeRequestFactory.create(
        repository=default_revision.repository,
        parent_ref=default_revision.sha,
        head_ref=None,
    )

    assert cr.parent_revision_sha is None
    assert cr.head_revision_sha is None

    resolve_ref_for_change_request(cr.id)

    assert cr.parent_revision_sha == default_revision.sha
    assert cr.head_revision_sha is None


def test_resolve_ref_for_change_request_parent_and_head(default_revision):
    cr = factories.ChangeRequestFactory.create(
        repository=default_revision.repository,
        parent_ref=default_revision.sha,
        head_ref=default_revision.sha,
    )

    assert cr.parent_revision_sha is None
    assert cr.head_revision_sha is None

    resolve_ref_for_change_request(cr.id)

    assert cr.parent_revision_sha == default_revision.sha
    assert cr.head_revision_sha == default_revision.sha
