from datetime import datetime, timezone
from flask import current_app

from zeus import auth
from zeus.config import celery, db
from zeus.models import Repository, RepositoryStatus


@celery.task(max_retries=None)
def import_repo(repo_id, parent=None):
    repo = Repository.query.unrestricted_unsafe().get(repo_id)
    if not repo:
        current_app.logger.error('Repository %s not found', repo_id)
        return

    auth.set_current_tenant(
        auth.Tenant(
            organization_ids=[repo.organization_id],
            repository_ids=[repo.id],
        )
    )

    vcs = repo.get_vcs()
    if vcs is None:
        current_app.logger.warning('Repository %s has no VCS backend set', repo.id)
        return

    if repo.status == RepositoryStatus.inactive:
        current_app.logger.info('Repository %s is inactive', repo.id)
        return

    Repository.query.filter(
        Repository.id == repo.id,
    ).update({
        'last_update_attempt': datetime.now(timezone.utc),
    })
    db.session.commit()

    if vcs.exists():
        vcs.update()
    else:
        vcs.clone()

    for commit in vcs.log(parent=parent):
        revision, created = commit.save(repo)
        db.session.commit()
        parent = commit.id

    Repository.query.filter(
        Repository.id == repo.id,
    ).update({
        'last_update': datetime.now(timezone.utc),
    })
    db.session.commit()

    if parent:
        import_repo.delay(
            repo_id=repo.id,
            parent=parent,
        )
