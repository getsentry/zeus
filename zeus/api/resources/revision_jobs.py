from sqlalchemy.orm import subqueryload_all

from zeus.models import Job, Revision
from zeus.utils.builds import fetch_build_for_revision

from .base_revision import BaseRevisionResource
from ..schemas import JobSchema

job_schema = JobSchema(strict=True)
jobs_schema = JobSchema(many=True, strict=True)


class RevisionJobsResource(BaseRevisionResource):
    def get(self, revision: Revision):
        """
        Return a list of jobs for a given revision.
        """
        build = fetch_build_for_revision(revision)
        if not build:
            return self.respond(status=404)

        build_ids = [original.id for original in build.original]
        query = (
            Job.query.options(subqueryload_all("stats"), subqueryload_all("failures"))
            .filter(Job.build_id.in_(build_ids))
            .order_by(Job.number.asc())
        )
        return self.respond_with_schema(jobs_schema, query)
