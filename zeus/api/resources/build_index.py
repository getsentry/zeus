from sqlalchemy.orm import joinedload, subqueryload_all

from zeus import auth
from zeus.models import Build

from .base import Resource
from ..schemas import BuildSchema

builds_schema = BuildSchema(many=True, strict=True)


class BuildIndexResource(Resource):
    def get(self):
        """
        Return a list of builds.
        """
        # tenants automatically restrict this query but we dont want
        # to include public repos
        tenant = auth.get_current_tenant()
        if not tenant.repository_ids:
            return self.respond([])

        query = (
            Build.query.options(
                joinedload("repository"),
                joinedload("source"),
                joinedload("source").joinedload("author"),
                joinedload("source").joinedload("revision"),
                joinedload("source").joinedload("patch"),
                subqueryload_all("stats"),
            )
            .filter(Build.repository_id.in_(tenant.repository_ids))
            .order_by(Build.date_created.desc())
        )
        return self.paginate_with_schema(builds_schema, query)
