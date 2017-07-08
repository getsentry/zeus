from zeus.models import Build

from .base import Resource
from ..schemas import BuildSchema

build_schema = BuildSchema(strict=True)


class BuildDetailsResource(Resource):
    def get(self, build_id):
        """
        Return a build.
        """
        build = Build.query.get(build_id)
        if not build:
            return self.not_found()
        return self.respond_with_schema(build_schema, build)
