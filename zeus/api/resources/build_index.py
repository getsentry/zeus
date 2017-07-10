from sqlalchemy.orm import joinedload, subqueryload_all

from zeus.models import Build

from .base import Resource
from ..schemas import BuildSchema

builds_schema = BuildSchema(many=True, strict=True)


class BuildIndexResource(Resource):
    def get(self):
        """
        Return a list of builds.
        """
        query = Build.query.options(
            joinedload('source').joinedload('revision'),
            subqueryload_all('stats'),
        ).order_by(Build.date_created.desc()).limit(100)
        return self.respond_with_schema(builds_schema, query)
