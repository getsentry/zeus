from uuid import UUID

from zeus.config import db
from zeus.models import ItemOption, Repository, RepositoryStatus


def disable_repo(repository_id: UUID, repository: Repository = None):
    if repository:
        repository.status = RepositoryStatus.inactive
    ItemOption.query.filter(
        ItemOption.item_id == repository_id, ItemOption.name == "auth.private-key"
    ).delete()
    db.session.add(repository)
    db.session.commit()
