import sentry_sdk

from uuid import UUID

from flask import current_app

from zeus import auth
from zeus.config import celery, db
from zeus.constants import Permission
from zeus.models import Build, Job, Repository, RepositoryStatus, ItemOption, ItemStat


@celery.task(name="zeus.delete_repo", max_retries=None, autoretry_for=(Exception,))
def delete_repo(repository_id: UUID):
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("repository_id", str(repository_id))

    auth.set_current_tenant(auth.RepositoryTenant(repository_id, Permission.admin))

    repo = Repository.query.unrestricted_unsafe().get(repository_id)
    if not repo:
        current_app.logger.error("Repository %s not found", repository_id)
        return

    if repo.status != RepositoryStatus.inactive:
        current_app.logger.error("Repository %s not marked as inactive", repository_id)
        return

    # delete repo abstract entities
    ItemOption.query.filter_by(item_id=repo.id).delete()
    ItemStat.query.filter_by(item_id=repo.id).delete()

    # delete related abstract entities (build/job)
    for model in ItemStat, ItemOption:
        model.query.filter(
            model.item_id.in_(
                db.session.query(Build.id)
                .filter(Build.repository_id == repo.id)
                .subquery()
            )
        ).delete(synchronize_session=False)
        model.query.filter(
            model.item_id.in_(
                db.session.query(Job.id).filter(Job.repository_id == repo.id).subquery()
            )
        ).delete(synchronize_session=False)

    db.session.delete(repo)
    db.session.commit()
