from zeus.models import Build

from .base import Resource
from ..schemas import BuildSchema

builds_schema = BuildSchema(many=True, strict=True)


class BuildIndexResource(Resource):
    def get(self):
        """
        Return a list of builds.
        """
        query = Build.query.all()
        return self.respond_with_schema(builds_schema, query)
