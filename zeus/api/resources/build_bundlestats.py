from sqlalchemy.orm import subqueryload_all

from zeus.config import db
from zeus.models import Job, Build, Bundle

from .base_build import BaseBuildResource
from ..schemas import BundleSchema

bundle_schema = BundleSchema(many=True, strict=True)


class BuildBundleStatsResource(BaseBuildResource):
    def get(self, build: Build):
        """
        Return bundle stats for a given build.
        """
        job_ids = db.session.query(Job.id).filter(
            Job.build_id == build.id,
        ).subquery()

        query = Bundle.query.filter(
            Bundle.job_id.in_(job_ids),
        ).options(
            subqueryload_all(Bundle.assets)
        ).order_by(
            Bundle.name.asc(),
        )

        return self.paginate_with_schema(bundle_schema, query)
