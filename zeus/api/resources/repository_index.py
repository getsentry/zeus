from zeus import auth
from zeus.config import db
from zeus.models import Repository, RepositoryAccess

from .base import Resource
from ..schemas import RepositorySchema

repo_schema = RepositorySchema(strict=True)
repos_schema = RepositorySchema(many=True, strict=True)


class RepositoryIndexResource(Resource):
    def get(self):
        """
        Return a list of repositories.
        """
        query = Repository.query.all()
        return self.respond_with_schema(repos_schema, query)

    def post(self):
        """
        Create a new repository
        """
        result = self.schema_from_request(repo_schema, partial=True)
        if result.errors:
            return self.respond(result.errors, 403)
        data = result.data
        repo = Repository(**data)
        db.session.add(repo)
        db.session.add(RepositoryAccess(
            repository=repo,
            user=auth.get_current_user(),
        ))
        db.session.commit()

        return self.respond_with_schema(repo_schema, repo)
