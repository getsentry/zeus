from datetime import datetime, timezone
from flask import current_app

from zeus import auth
from zeus.config import celery, db
from zeus.constants import Permission
from zeus.exceptions import UnknownRepositoryBackend
from zeus.models import Repository, RepositoryStatus


@celery.task(max_retries=5, autoretry_for=(Exception,))
def import_repo(repo_id, parent=None):
    auth.set_current_tenant(auth.Tenant(access={repo_id: Permission.admin}))

    repo = Repository.query.get(repo_id)
    if not repo:
        current_app.logger.error("Repository %s not found", repo_id)
        return

    try:
        vcs = repo.get_vcs()
    except UnknownRepositoryBackend:
        current_app.logger.warning("Repository %s has no VCS backend set", repo.id)
        return

    if repo.status == RepositoryStatus.inactive:
        current_app.logger.info("Repository %s is inactive", repo.id)
        return

    Repository.query.filter(Repository.id == repo.id).update(
        {"last_update_attempt": datetime.now(timezone.utc)}
    )
    db.session.commit()

    if vcs.ensure():
        vcs.update()
    else:
        vcs.clone()

    has_more = False
    for commit in vcs.log(parent=parent):
        revision, created = commit.save(repo)
        db.session.commit()
        if parent == commit.sha:
            break

        parent = commit.sha
        has_more = True

    Repository.query.filter(Repository.id == repo.id).update(
        {"last_update": datetime.now(timezone.utc)}
    )
    db.session.commit()

    if has_more:
        import_repo.delay(repo_id=repo.id, parent=parent)
