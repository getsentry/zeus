from zeus.models import Build, Repository

from .base import Resource
from ..schemas import BuildSchema

build_schema = BuildSchema(strict=True)


class BuildDetailsResource(Resource):
    def get(self, repository_name: str, build_number: int):
        """
        Return a build.
        """
        build = Build.query.join(Repository, Repository.id == Build.repository_id).filter(
            Repository.name == repository_name,
            Build.number == build_number,
        ).first()
        if not build:
            return self.not_found()
        return self.respond_with_schema(build_schema, build)
