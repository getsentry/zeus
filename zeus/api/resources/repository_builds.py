from sqlalchemy.orm import joinedload

from zeus.models import Build, Repository

from .base import Resource
from ..schemas import BuildSchema

builds_schema = BuildSchema(many=True, strict=True)


class RepositoryBuildsResource(Resource):
    def get(self, repository_name: str):
        """
        Return a list of builds for the given repository.
        """
        repo = Repository.query.filter(Repository.name == repository_name).first()
        if not repo:
            return self.not_found()

        query = Build.query.options(
            joinedload('source').joinedload('revision'),
        ).filter(
            Build.repository_id == repo.id,
        ).order_by(Build.number.desc()).limit(100)
        return self.respond_with_schema(builds_schema, query)
