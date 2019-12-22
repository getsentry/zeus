from sqlalchemy import or_

from zeus.config import celery
from zeus.models import Repository, RepositoryStatus
from zeus.utils import timezone

from .sync_repo import sync_repo


@celery.task(name="zeus.sync_all_repos", time_limit=300)
def sync_all_repos():
    queryset = (
        Repository.query.unrestricted_unsafe()
        .filter(
            Repository.status == RepositoryStatus.active,
            or_(
                Repository.next_update < timezone.now(),
                Repository.next_update == None,  # NOQA
            ),
        )
        .limit(100)
    )

    for repo in queryset:
        sync_repo.delay(repo_id=repo.id)
