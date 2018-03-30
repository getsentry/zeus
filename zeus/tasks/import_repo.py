from datetime import datetime, timezone
from flask import current_app

from zeus import auth
from zeus.config import celery, db
from zeus.constants import Permission
from zeus.db.types import GUID
from zeus.models import Repository, RepositoryRef, RepositoryStatus, RepositoryTree


@celery.task(max_retries=None, autoretry_for=(Exception,))
def import_repo(repo_id: GUID, parent: str = None):
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

    Repository.query.filter(Repository.id == repo.id).update(
        {"last_update_attempt": datetime.now(timezone.utc)}
    )
    db.session.commit()

    if vcs.exists():
        vcs.update()
    else:
        vcs.clone()

    # TODO(dcramer): what if we didnt import all commits and just imported
    # the default tree instead?
    has_more = False
    for commit in vcs.log(parent=parent):
        revision, created = commit.save(repo)
        db.session.commit()
        if parent == revision.sha:
            break

        parent = revision.sha
        has_more = True

    Repository.query.filter(Repository.id == repo.id).update(
        {"last_update": datetime.now(timezone.utc)}
    )
    db.session.commit()

    if has_more:
        import_repo.delay(repo_id=repo.id, parent=parent)
    else:
        import_ref.delay(repo_id=repo.id, name=vcs.get_default_branch())


@celery.task(max_retries=None, autoretry_for=(Exception,))
def import_ref(repo_id: GUID, name: str, parent: str = None):
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

    if vcs.exists():
        vcs.update()
    else:
        vcs.clone()

    ref = RepositoryRef.get(repo_id, name)

    child_revisions = []
    current_parent = parent
    has_more = False
    for commit in vcs.log(parent=current_parent, branch=ref.name):
        revision, created = commit.save(repo)
        db.session.commit()
        if current_parent == revision.sha:
            break

        child_revisions.append(revision.sha)
        current_parent = revision.sha
        has_more = True

    RepositoryTree.prepend_tree(
        repository_id=repo.id,
        ref_id=ref.id,
        parent_sha=parent,
        new_revisions=child_revisions,
    )

    if has_more:
        import_ref.delay(repo_id=repo.id, name=name, parent=current_parent)
