from zeus.models import Build

from .base_build import BaseBuildResource
from ..schemas import BuildSchema

build_schema = BuildSchema(strict=True)


class BuildDetailsResource(BaseBuildResource):
    def get(self, build: Build):
        """
        Return a build.
        """
        return self.respond_with_schema(build_schema, build)
