from zeus.config import db
from zeus.db.func import array_agg_row
from zeus.models import Job, Build, BundleEntrypoint

from .base_build import BaseBuildResource
from ..schemas import AggregateBundleEntrypointSchema

bundle_entrypoint_schema = AggregateBundleEntrypointSchema(
    many=True, strict=True)


class BuildBundleStatsResource(BaseBuildResource):
    def get(self, build: Build):
        """
        Return bundle stats for a given build.
        """
        job_ids = db.session.query(Job.id).filter(
            Job.build_id == build.id,
        ).subquery()

        query = db.session.query(
            BundleEntrypoint.name,
            array_agg_row(BundleEntrypoint.id,
                          BundleEntrypoint.job_id).label('results'),
        ).filter(
            BundleEntrypoint.job_id.in_(job_ids),
        ).group_by(BundleEntrypoint.name)

        query = query.order_by(
            BundleEntrypoint.name.asc(),
        )

        return self.paginate_with_schema(bundle_entrypoint_schema, query)
