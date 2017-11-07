from zeus.config import db
from zeus.models import Hook, Repository

from .base_repository import BaseRepositoryResource
from ..schemas import HookSchema

hook_schema = HookSchema(strict=True)
hooks_schema = HookSchema(many=True, strict=True)


class RepositoryHooksResource(BaseRepositoryResource):
    def select_resurce_for_update(self):
        return False

    def get(self, repo: Repository):
        """
        Return a list of hooks for the given repository.
        """
        query = Hook.query.filter(
            Hook.repository_id == repo.id,
        ).order_by(Hook.date_created.desc())

        return self.paginate_with_schema(hooks_schema, query)

    def post(self, repo: Repository):
        """
        Create a new hook.
        """
        result = self.schema_from_request(hook_schema)
        if result.errors:
            return self.respond(result.errors, 403)
        hook = result.data
        hook.repository = repo
        db.session.add(hook)
        db.session.commit()

        return self.respond_with_schema(hook_schema, hook)
