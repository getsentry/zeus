from datetime import timedelta
from flask import current_app

from zeus import auth
from zeus.config import celery, db
from zeus.constants import Permission
from zeus.exceptions import UnknownRepositoryBackend
from zeus.models import ItemOption, Repository, RepositoryStatus
from zeus.utils import timezone
from zeus.vcs.base import InvalidPublicKey


# TODO(dcramer): a lot of this code is shared with import_repo


@celery.task(max_retries=5, autoretry_for=(Exception,), acks_late=True)
def sync_repo(repo_id, max_log_passes=10, force=False, time_limit=300):
    auth.set_current_tenant(auth.Tenant(access={repo_id: Permission.admin}))

    repo = Repository.query.get(repo_id)
    if not repo:
        current_app.logger.error("Repository %s not found", repo_id)
        return

    if (
        not force
        and repo.last_update_attempt
        and repo.last_update_attempt
        > (timezone.now() - current_app.config["REPO_MIN_SYNC_INTERVAL"])
    ):
        current_app.logger.warning(
            "Repository %s was synced recently, refusing to sync", repo.id
        )
        return

    try:
        vcs = repo.get_vcs()
    except UnknownRepositoryBackend:
        current_app.logger.warning("Repository %s has no VCS backend set", repo.id)
        return

    if repo.status != RepositoryStatus.active:
        current_app.logger.info("Repository %s is not active", repo.id)
        return

    Repository.query.filter(Repository.id == repo.id).update(
        {"last_update_attempt": timezone.now()}
    )
    db.session.commit()

    try:
        if vcs.exists():
            vcs.update(allow_cleanup=True)
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

    # TODO(dcramer): this doesn't collect commits in non-default branches
    might_have_more = True
    parent = None
    had_results = False
    while might_have_more and max_log_passes:
        might_have_more = False
        for commit in vcs.log(parent=parent):
            revision, created = commit.save(repo)
            db.session.commit()
            if not created:
                break

            had_results = True

            current_app.logger.info("Created revision {}".format(repo.id))
            might_have_more = True
            parent = commit.sha
        max_log_passes -= 1

    now = timezone.now()
    next_update = now + current_app.config["REPO_MIN_SYNC_INTERVAL"]
    if repo.last_update and not had_results:
        time_since_last_update = now - repo.last_update
        next_update += min(
            time_since_last_update,
            timedelta(current_app.config["REPO_MAX_SYNC_INTERVAL"]),
        )

    Repository.query.filter(Repository.id == repo.id).update(
        {"last_update": now, "next_update": next_update}
    )
    db.session.commit()

    # is there more data to sync?
    return might_have_more
