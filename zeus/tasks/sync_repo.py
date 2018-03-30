from datetime import datetime
from flask import current_app

from zeus import auth
from zeus.config import celery, db
from zeus.constants import Permission
from zeus.db.types import GUID
from zeus.models import (
    ItemOption,
    Repository,
    RepositoryRef,
    RepositoryStatus,
    RepositoryTree,
)
from zeus.utils import timezone
from zeus.vcs.base import InvalidPublicKey


# TODO(dcramer): a lot of this code is shared with import_repo
def update_repo(repo, vcs):
    try:
        if vcs.exists():
            vcs.update()
        else:
            vcs.clone()
    except InvalidPublicKey:
        # TODO(dcramer): this is a quick short-circuit for repo syncing, which will
        # at least prevent workers from endlessly querying repos which were revoked.
        # Ideally this would be implemented in a larger number of places (maybe via
        # a context manager?)
        repo.status = RepositoryStatus.inactive
        ItemOption.query.filter(
            ItemOption.item_id == repo.id, ItemOption.name == "auth.private-key"
        ).delete()
        db.session.add(repo)
        db.session.commit()
        return


@celery.task(max_retries=None, autoretry_for=(Exception,), acks_late=True)
def sync_repo(repo_id: GUID, max_log_passes=10):
    auth.set_current_tenant(auth.Tenant(access={repo_id: Permission.admin}))

    repo = Repository.query.get(repo_id)
    if not repo:
        current_app.logger.error("Repository %s not found", repo_id)
        return

    vcs = repo.get_vcs()
    if vcs is None:
        current_app.logger.warning("Repository %s has no VCS backend set", repo.id)
        return

    if repo.status != RepositoryStatus.active:
        current_app.logger.info("Repository %s is not active", repo.id)
        return

    Repository.query.filter(Repository.id == repo.id).update(
        {"last_update_attempt": timezone.now()}
    )
    db.session.commit()

    update_repo(repo, vcs)

    # TODO(dcramer): this doesn't collect commits in non-default branches
    might_have_more = True
    parent = None
    while might_have_more and max_log_passes:
        might_have_more = False
        for commit in vcs.log(parent=parent):
            revision, created = commit.save(repo)
            db.session.commit()
            if not created:
                break

            current_app.logger.info("Created revision {}".format(repo.id))
            might_have_more = True
            parent = commit.sha
        max_log_passes -= 1

    Repository.query.filter(Repository.id == repo.id).update(
        {"last_update": datetime.now(timezone.utc)}
    )
    db.session.commit()

    # is there more data to sync?
    return might_have_more


@celery.task(max_retries=None, autoretry_for=(Exception,))
def sync_ref(repo_id: GUID, name: str, max_log_passes=10):
    auth.set_current_tenant(auth.Tenant(access={repo_id: Permission.admin}))

    repo = Repository.query.get(repo_id)
    if not repo:
        current_app.logger.error("Repository %s not found", repo_id)
        return

    vcs = repo.get_vcs()
    if vcs is None:
        current_app.logger.warning("Repository %s has no VCS backend set", repo.id)
        return

    if repo.status == RepositoryStatus.inactive:
        current_app.logger.info("Repository %s is inactive", repo.id)
        return

    update_repo(repo, vcs)

    ref = RepositoryRef.get(repo_id, name)

    child_revisions = []
    parent = (
        db.session.query(RepositoryTree.revision_sha)
        .filter(ref_id=ref.id)
        .order_by(RepositoryTree.order.desc().first())
    )[0]
    # TODO(dcramer): this doesn't collect commits in non-default branches
    might_have_more = True
    current_parent = parent
    while might_have_more and max_log_passes:
        might_have_more = False
        for commit in vcs.log(branch=ref.name):
            revision, created = commit.save(repo)
            db.session.commit()
            if created:
                current_app.logger.info("Created revision {}".format(repo.id))
            might_have_more = True
            child_revisions.append(revision.sha)
            current_parent = commit.sha
            if current_parent == parent:
                break
        max_log_passes -= 1

    # we currently cannot handle gaps
    if current_parent != parent:
        raise NotImplementedError
    RepositoryTree.append_tree(
        repository_id=repo.id,
        ref_id=ref.id,
        parent_sha=child_revisions[0],
        new_revisions=child_revisions[1:].reverse(),
    )

    return might_have_more
