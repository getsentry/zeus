from zeus import auth, factories
from zeus.constants import Permission
from zeus.models import RepositoryRef, RepositoryTree


def test_append_tree_with_parent(db_session, default_repo):
    auth.set_current_tenant(auth.Tenant(access={default_repo.id: Permission.admin}))
    ref = RepositoryRef(repository=default_repo, name="master")
    db_session.add(ref)

    parent_revision = factories.RevisionFactory(repository=default_repo)
    child_revision = factories.RevisionFactory(repository=default_repo)

    tree = RepositoryTree(
        repository=default_repo, ref=ref, revision_sha=parent_revision.sha, order=0
    )
    db_session.add(tree)

    db_session.flush()

    RepositoryTree.append_tree(
        repository_id=default_repo.id,
        ref_id=ref.id,
        parent_sha=parent_revision.sha,
        new_revisions=[child_revision.sha],
    )

    results = list(
        RepositoryTree.query.filter(
            RepositoryTree.repository_id == default_repo.id
        ).order_by(RepositoryTree.order)
    )
    assert len(results) == 2
    assert results[0].revision_sha == parent_revision.sha
    assert results[0].order == 0
    assert results[1].revision_sha == child_revision.sha
    assert results[1].order == 1

    RepositoryTree.append_tree(
        repository_id=default_repo.id,
        ref_id=ref.id,
        parent_sha=parent_revision.sha,
        new_revisions=[child_revision.sha],
    )

    results = list(
        RepositoryTree.query.filter(
            RepositoryTree.repository_id == default_repo.id
        ).order_by(RepositoryTree.order)
    )
    assert len(results) == 2
    assert results[0].revision_sha == parent_revision.sha
    assert results[0].order == 0
    assert results[1].revision_sha == child_revision.sha
    assert results[1].order == 1

    RepositoryTree.append_tree(
        repository_id=default_repo.id,
        ref_id=ref.id,
        parent_sha=parent_revision.sha,
        new_revisions=[],
    )

    results = list(
        RepositoryTree.query.filter(
            RepositoryTree.repository_id == default_repo.id
        ).order_by(RepositoryTree.order)
    )
    assert len(results) == 1
    assert results[0].revision_sha == parent_revision.sha
    assert results[0].order == 0


def test_append_tree_with_empty_parent(db_session, default_repo):
    auth.set_current_tenant(auth.Tenant(access={default_repo.id: Permission.admin}))
    ref = RepositoryRef(repository=default_repo, name="master")
    db_session.add(ref)

    parent_revision = factories.RevisionFactory(repository=default_repo)
    child_revision = factories.RevisionFactory(repository=default_repo)

    db_session.flush()

    RepositoryTree.append_tree(
        repository_id=default_repo.id,
        ref_id=ref.id,
        new_revisions=[parent_revision.sha, child_revision.sha],
    )

    results = list(
        RepositoryTree.query.filter(
            RepositoryTree.repository_id == default_repo.id
        ).order_by(RepositoryTree.order)
    )
    assert len(results) == 2
    assert results[0].revision_sha == parent_revision.sha
    assert results[0].order == 0
    assert results[1].revision_sha == child_revision.sha
    assert results[1].order == 1

    RepositoryTree.append_tree(
        repository_id=default_repo.id,
        ref_id=ref.id,
        new_revisions=[parent_revision.sha, child_revision.sha],
    )

    results = list(
        RepositoryTree.query.filter(
            RepositoryTree.repository_id == default_repo.id
        ).order_by(RepositoryTree.order)
    )
    assert len(results) == 2
    assert results[0].revision_sha == parent_revision.sha
    assert results[0].order == 0
    assert results[1].revision_sha == child_revision.sha
    assert results[1].order == 1

    RepositoryTree.append_tree(
        repository_id=default_repo.id, ref_id=ref.id, new_revisions=[child_revision.sha]
    )

    results = list(
        RepositoryTree.query.filter(
            RepositoryTree.repository_id == default_repo.id
        ).order_by(RepositoryTree.order)
    )
    assert len(results) == 1
    assert results[0].revision_sha == child_revision.sha
    assert results[0].order == 0


def test_prepend_tree_with_parent(db_session, default_repo):
    auth.set_current_tenant(auth.Tenant(access={default_repo.id: Permission.admin}))
    ref = RepositoryRef(repository=default_repo, name="master")
    db_session.add(ref)

    parent_revision = factories.RevisionFactory(repository=default_repo)
    child_revision = factories.RevisionFactory(repository=default_repo)
    grandchild_revision = factories.RevisionFactory(repository=default_repo)
    db_session.flush()

    RepositoryTree.prepend_tree(
        repository_id=default_repo.id,
        ref_id=ref.id,
        parent_sha=grandchild_revision.sha,
        new_revisions=[child_revision.sha],
    )

    results = list(
        RepositoryTree.query.filter(
            RepositoryTree.repository_id == default_repo.id
        ).order_by(RepositoryTree.order)
    )
    assert len(results) == 2
    assert results[0].revision_sha == child_revision.sha
    assert results[0].order == -1
    assert results[1].revision_sha == grandchild_revision.sha
    assert results[1].order == 0

    RepositoryTree.prepend_tree(
        repository_id=default_repo.id,
        ref_id=ref.id,
        parent_sha=grandchild_revision.sha,
        new_revisions=[child_revision.sha],
    )

    results = list(
        RepositoryTree.query.filter(
            RepositoryTree.repository_id == default_repo.id
        ).order_by(RepositoryTree.order)
    )
    assert len(results) == 2
    assert results[0].revision_sha == child_revision.sha
    assert results[0].order == -1
    assert results[1].revision_sha == grandchild_revision.sha
    assert results[1].order == 0

    RepositoryTree.prepend_tree(
        repository_id=default_repo.id,
        ref_id=ref.id,
        parent_sha=grandchild_revision.sha,
        new_revisions=[child_revision.sha, parent_revision.sha],
    )

    results = list(
        RepositoryTree.query.filter(
            RepositoryTree.repository_id == default_repo.id
        ).order_by(RepositoryTree.order)
    )
    assert len(results) == 3
    assert results[0].revision_sha == parent_revision.sha
    assert results[0].order == -2
    assert results[1].revision_sha == child_revision.sha
    assert results[1].order == -1
    assert results[2].revision_sha == grandchild_revision.sha
    assert results[2].order == 0

    RepositoryTree.prepend_tree(
        repository_id=default_repo.id,
        ref_id=ref.id,
        parent_sha=child_revision.sha,
        new_revisions=[],
    )

    results = list(
        RepositoryTree.query.filter(
            RepositoryTree.repository_id == default_repo.id
        ).order_by(RepositoryTree.order)
    )
    assert len(results) == 2
    assert results[0].revision_sha == child_revision.sha
    assert results[0].order == -1
    assert results[1].revision_sha == grandchild_revision.sha
    assert results[1].order == 0

    RepositoryTree.prepend_tree(
        repository_id=default_repo.id,
        ref_id=ref.id,
        parent_sha=grandchild_revision.sha,
        new_revisions=[],
    )

    results = list(
        RepositoryTree.query.filter(
            RepositoryTree.repository_id == default_repo.id
        ).order_by(RepositoryTree.order)
    )
    assert len(results) == 1
    assert results[0].revision_sha == grandchild_revision.sha
    assert results[0].order == 0
