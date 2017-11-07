from datetime import timedelta

from zeus.config import celery, db
from zeus.models import Repository, RepositoryStatus
from zeus.utils import timezone

from .sync_repo import sync_repo


@celery.task(max_retries=None)
def sync_all_repos():
    queryset = Repository.query.unrestricted_unsafe().filter(
        Repository.status == RepositoryStatus.active,
        Repository.last_update_attempt < (
            timezone.now() - timedelta(minutes=5))
    )

    for repo in queryset:
        sync_repo.delay(
            repo_id=repo.id,
        )
        Repository.query.filter(
            Repository.id == repo.id,
        ).update({
            'last_update_attempt': timezone.now(),
        })
        db.session.commit()
