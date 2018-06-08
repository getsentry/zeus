from zeus import auth
from zeus.models import Repository

from .base import Resource
from ..schemas import RepositorySchema


class RepositoryIndexResource(Resource):
    def get(self):
        """
        Return a list of repositories.
        """
        tenant = auth.get_current_tenant()
        if not tenant.repository_ids:
            return self.respond([])

        query = (
            Repository.query.filter(Repository.id.in_(tenant.repository_ids))
            .order_by(Repository.owner_name.asc(), Repository.name.asc())
            .limit(100)
        )
        schema = RepositorySchema(
            many=True, strict=True, context={"user": auth.get_current_user()}
        )
        return self.paginate_with_schema(schema, query)
