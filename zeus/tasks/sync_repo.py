from datetime import datetime
from flask import current_app

from zeus import auth
from zeus.config import celery, db
from zeus.models import Repository, RepositoryStatus
from zeus.utils import timezone


# TODO(dcramer): a lot of this code is shared with import_repo
@celery.task(max_retries=None, autoretry_for=(Exception,), acks_late=True)
def sync_repo(repo_id, max_log_passes=10):
    auth.set_current_tenant(auth.Tenant(repository_ids=[repo_id]))

    repo = Repository.query.get(repo_id)
    if not repo:
        current_app.logger.error('Repository %s not found', repo_id)
        return

    vcs = repo.get_vcs()
    if vcs is None:
        current_app.logger.warning(
            'Repository %s has no VCS backend set', repo.id)
        return

    if repo.status != RepositoryStatus.active:
        current_app.logger.info('Repository %s is not active', repo.id)
        return

    Repository.query.filter(
        Repository.id == repo.id,
    ).update({
        'last_update_attempt': timezone.now(),
    })
    db.session.commit()

    if vcs.exists():
        vcs.update()
    else:
        vcs.clone()

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

            current_app.logger.info('Created revision {}'.format(repo.id))
            might_have_more = True
            parent = commit.sha
        max_log_passes -= 1

    Repository.query.filter(
        Repository.id == repo.id,
    ).update({
        'last_update': datetime.now(timezone.utc),
    })
    db.session.commit()

    # is there more data to sync?
    return might_have_more
