from sqlalchemy.orm import joinedload

from zeus.config import db, nplusone
from zeus.models import Build, ItemStat, Source
from zeus.pubsub.utils import publish

from .base_build import BaseBuildResource
from ..schemas import BuildSchema

build_schema = BuildSchema(strict=True)


class BuildDetailsResource(BaseBuildResource):

    def select_resource_for_update(self) -> bool:
        return self.is_mutation()

    def get(self, build: Build):
        """
        Return a build.
        """
        with nplusone.ignore("eager_load"):
            build.source = Source.query.options(
                joinedload("revision"), joinedload("patch")
            ).get(
                build.source_id
            )
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

        result = build_schema.dump(build)
        if result.errors:
            return self.error("invalid schema supplied")

        publish("builds", "build.update", result.data)
        return self.respond(result.data, 200)
