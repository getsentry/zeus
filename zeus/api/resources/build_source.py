from sqlalchemy.orm import joinedload, undefer
from zeus.models import Build, Source

from .base_build import BaseBuildResource
from ..schemas import SourceSchema

source_schema = SourceSchema()


class BuildSourceResource(BaseBuildResource):
    def get(self, build: Build):
        """
        Return a source for the given build.
        """
        source = Source.query.options(joinedload("patch"), undefer("patch.diff")).get(
            build.source_id
        )
        if source is None:
            return self.not_found()

        return self.respond_with_schema(source_schema, source)
