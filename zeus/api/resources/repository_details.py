from zeus.config import db
from zeus.constants import Permission
from zeus.models import Repository

from .base_repository import BaseRepositoryResource
from ..schemas import RepositorySchema


class RepositoryDetailsResource(BaseRepositoryResource):
    permission_overrides = {
        'PUT': Permission.admin,
    }

    def select_resurce_for_update(self) -> bool:
        return self.is_mutation()

    def get(self, repo: Repository):
        """
        Return a repository.
        """
        schema = RepositorySchema(strict=True)
        return self.respond_with_schema(schema, repo)

    def put(self, repo: Repository):
        """
        Return a repository.
        """
        schema = RepositorySchema(
            strict=True, partial=True, context={'repository': repo})
        result = self.schema_from_request(schema)
        if result.errors:
            return self.respond(result.errors, 403)

        if db.session.is_modified(repo):
            db.session.add(repo)
            db.session.commit()

        return self.respond_with_schema(schema, repo)
