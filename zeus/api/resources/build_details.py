from zeus.config import db, nplusone
from zeus.models import Build, ItemStat, Revision
from zeus.pubsub.utils import publish

from .base_build import BaseBuildResource
from ..schemas import BuildSchema

build_schema = BuildSchema()


class BuildDetailsResource(BaseBuildResource):
    def select_resource_for_update(self) -> bool:
        return self.is_mutation()

    def get(self, build: Build):
        """
        Return a build.
        """
        with nplusone.ignore("eager_load"):
            build.revision = Revision.query.filter(
                Revision.sha == build.revision_sha,
                Revision.repository_id == build.repository_id,
            ).first()
        build.stats = list(ItemStat.query.filter(ItemStat.item_id == build.id))
        return self.respond_with_schema(build_schema, build)

    def put(self, build: Build):
        """
        Update a build.
        """
        result = self.schema_from_request(build_schema, partial=True)

        for key, value in result.items():
            if getattr(build, key) != value:
                setattr(build, key, value)
        if db.session.is_modified(build):
            db.session.add(build)
            db.session.commit()

        result = build_schema.dump(build)
        publish("builds", "build.update", result)
        return self.respond(result, 200)
