from uuid import UUID

from flask import current_app

from zeus import auth
from zeus.config import celery, db, redis
from zeus.constants import Permission
from zeus.models import Repository, ItemOption, RepositoryAccess


@celery.task(name="zeus.delete_repo")
def delete_repo(repo_id: UUID):
    auth.set_current_tenant(auth.Tenant(access={repo_id: Permission.admin}))

    repo = Repository.query.unrestricted_unsafe().get(repo_id)
    if not repo:
        current_app.logger.error("Repository %s not found", repo_id)
        return

    lock_key = Repository.get_lock_key(repo.owner_name, repo.name)
    with redis.lock(lock_key):
        ItemOption.query.filter_by(item_id=repo.id, name="auth.private-key").delete()
        RepositoryAccess.query.filter_by(repository_id=repo.id).delete()
        db.session.delete(repo)
        db.session.commit()
