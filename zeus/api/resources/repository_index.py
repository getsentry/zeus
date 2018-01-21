from zeus import auth
from zeus.models import Repository

from .base import Resource
from ..schemas import RepositorySchema

repos_schema = RepositorySchema(many=True, strict=True)


class RepositoryIndexResource(Resource):
    def get(self):
        """
        Return a list of repositories.
        """
        tenant = auth.get_current_tenant()
        if not tenant.repository_ids:
            return self.respond([])
        query = Repository.query.filter(
            Repository.id.in_(tenant.repository_ids),
        ).order_by(Repository.owner_name.asc(), Repository.name.asc()).limit(100)
        return self.paginate_with_schema(repos_schema, query)
