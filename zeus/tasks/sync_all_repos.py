from datetime import timedelta
from sqlalchemy import or_

from zeus.config import celery, db
from zeus.models import Repository, RepositoryStatus
from zeus.utils import timezone

from .sync_repo import sync_repo


@celery.task(name="zeus.sync_all_repos")
def sync_all_repos():
    queryset = Repository.query.unrestricted_unsafe().filter(
        Repository.status == RepositoryStatus.active,
        or_(
            Repository.last_update_attempt < (timezone.now() - timedelta(minutes=5)),
            Repository.last_update_attempt is None,
        ),
    )

    for repo in queryset:
        sync_repo.delay(repo_id=repo.id)
        Repository.query.filter(Repository.id == repo.id).update(
            {"last_update_attempt": timezone.now()}
        )
        db.session.commit()
