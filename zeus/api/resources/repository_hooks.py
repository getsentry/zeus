from zeus.config import db
from zeus.constants import Permission
from zeus.models import Hook, Repository

from .base_repository import BaseRepositoryResource
from ..schemas import HookSchema

hook_schema = HookSchema()
hooks_schema = HookSchema(many=True)


class RepositoryHooksResource(BaseRepositoryResource):
    permission_overrides = {
        "DELETE": Permission.admin,
        "GET": Permission.admin,
        "PUT": Permission.admin,
        "POST": Permission.admin,
    }

    def select_resource_for_update(self):
        return False

    def get(self, repo: Repository):
        """
        Return a list of hooks for the given repository.
        """
        query = Hook.query.filter(Hook.repository_id == repo.id).order_by(
            Hook.date_created.desc()
        )

        return self.paginate_with_schema(hooks_schema, query)

    def post(self, repo: Repository):
        """
        Create a new hook.
        """
        hook = self.schema_from_request(hook_schema)
        hook.repository = repo
        db.session.add(hook)
        db.session.commit()

        return self.respond_with_schema(hook_schema, hook)
