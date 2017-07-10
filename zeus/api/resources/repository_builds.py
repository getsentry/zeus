from sqlalchemy.orm import joinedload, subqueryload_all

from zeus.models import Build, Repository

from .base_repository import BaseRepositoryResource
from ..schemas import BuildSchema

builds_schema = BuildSchema(many=True, strict=True)


class RepositoryBuildsResource(BaseRepositoryResource):
    def get(self, repo: Repository):
        """
        Return a list of builds for the given repository.
        """
        query = Build.query.options(
            joinedload('source').joinedload('revision'),
            joinedload('author'),
            subqueryload_all('stats'),
        ).filter(
            Build.repository_id == repo.id,
        ).order_by(Build.number.desc()).limit(100)
        return self.respond_with_schema(builds_schema, query)
