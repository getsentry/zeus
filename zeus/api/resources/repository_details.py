from zeus import auth
from zeus.config import celery, db
from zeus.constants import Permission
from zeus.models import Repository, RepositoryStatus

from .base_repository import BaseRepositoryResource
from ..schemas import RepositorySchema


class RepositoryDetailsResource(BaseRepositoryResource):
    permission_overrides = {"PUT": Permission.admin}

    def select_resource_for_update(self) -> bool:
        return self.is_mutation()

    def get(self, repo: Repository):
        """
        Return a repository.
        """
        schema = RepositorySchema(context={"user": auth.get_current_user()})
        return self.respond_with_schema(schema, repo)

    def put(self, repo: Repository):
        """
        Return a repository.
        """
        schema = RepositorySchema(
            partial=True, context={"repository": repo, "user": auth.get_current_user()}
        )
        self.schema_from_request(schema)

        if db.session.is_modified(repo):
            db.session.add(repo)
            db.session.commit()

        return self.respond_with_schema(schema, repo)

    def delete(self, repo: Repository):
        """
        Deactivate a repository.
        """
        if repo.status == RepositoryStatus.inactive:
            return self.respond(status=202)

        with db.session.begin_nested():
            repo.status = RepositoryStatus.inactive
            db.session.add(repo)
            db.session.flush()

            celery.delay("zeus.delete_repo", repo_id=repo.id)

        return self.respond(status=202)
