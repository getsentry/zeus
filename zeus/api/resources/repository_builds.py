from zeus.models import Build, Repository

from .base import Resource
from ..schemas import BuildSchema

builds_schema = BuildSchema(many=True, strict=True)


class RepositoryBuildsResource(Resource):
    def get(self, repository_id):
        """
        Return a list of builds for the given repository.
        """
        repo = Repository.query.get(repository_id)
        if not repo:
            return self.not_found()

        query = Build.query.filter(
            Build.repository_id == repository_id,
        )
        return self.respond_with_schema(builds_schema, query)
