from zeus.models import Repository

from .base_repository import BaseRepositoryResource
from ..schemas import RepositorySchema

repo_schema = RepositorySchema(strict=True)


class RepositoryDetailsResource(BaseRepositoryResource):
    def select_resurce_for_update(self) -> bool:
        return self.is_mutation()

    def get(self, repo: Repository):
        """
        Return a repository.
        """
        return self.respond_with_schema(repo_schema, repo)
