from sqlalchemy.orm import joinedload

from zeus.config import db
from zeus.models import Build, ItemStat, Source

from .base_build import BaseBuildResource
from ..schemas import BuildSchema

build_schema = BuildSchema(strict=True)


class BuildDetailsResource(BaseBuildResource):
    def select_resurce_for_update(self) -> bool:
        return self.is_mutation()

    def get(self, build: Build):
        """
        Return a build.
        """
        build.source = Source.query.options(joinedload('revision'),
                                            joinedload('patch')).get(build.source_id)
        build.stats = list(ItemStat.query.filter(ItemStat.item_id == build.id))
        return self.respond_with_schema(build_schema, build)

    def put(self, build: Build):
        """
        Update a build.
        """
        result = self.schema_from_request(build_schema, partial=True)
        if result.errors:
            return self.respond(result.errors, 403)
        for key, value in result.data.items():
            if getattr(build, key) != value:
                setattr(build, key, value)
        if db.session.is_modified(build):
            db.session.add(build)
            db.session.commit()

        return self.respond_with_schema(build_schema, build)
