from sqlalchemy.orm import subqueryload_all

from zeus.config import db
from zeus.models import Job, Revision, Bundle
from zeus.utils.builds import fetch_build_for_revision

from .base_revision import BaseRevisionResource
from ..schemas import BundleSchema

bundle_schema = BundleSchema(many=True)


class RevisionBundleStatsResource(BaseRevisionResource):
    def get(self, revision: Revision):
        """
        Return bundle stats for a given revision.
        """
        build = fetch_build_for_revision(revision)
        if not build:
            return self.respond(status=404)

        build_ids = [original.id for original in build.original]

        job_ids = (
            db.session.query(Job.id).filter(Job.build_id.in_(build_ids)).subquery()
        )

        query = (
            Bundle.query.filter(Bundle.job_id.in_(job_ids))
            .options(subqueryload_all(Bundle.assets))
            .order_by(Bundle.name.asc())
        )

        return self.paginate_with_schema(bundle_schema, query)
