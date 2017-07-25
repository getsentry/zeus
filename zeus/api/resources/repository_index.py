from zeus.models import Repository

from .base import Resource
from ..schemas import RepositorySchema

repos_schema = RepositorySchema(many=True, strict=True)


class RepositoryIndexResource(Resource):
    def get(self):
        """
        Return a list of repositories.
        """
        query = Repository.query
        return self.paginate_with_schema(repos_schema, query)
