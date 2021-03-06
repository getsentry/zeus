from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import subqueryload_all

from zeus.config import celery, db
from zeus.constants import Status
from zeus.models import Build, Job
from zeus.utils import timezone

from .base_build import BaseBuildResource
from ..schemas import JobSchema

job_schema = JobSchema()
jobs_schema = JobSchema(many=True)


class BuildJobsResource(BaseBuildResource):
    def get(self, build: Build):
        """
        Return a list of jobs for a given build.
        """
        query = (
            Job.query.options(subqueryload_all("stats"), subqueryload_all("failures"))
            .filter(Job.build_id == build.id)
            .order_by(Job.number.asc())
        )
        return self.respond_with_schema(jobs_schema, query)

    def post(self, build: Build):
        """
        Create a new job.
        """
        data = self.schema_from_request(job_schema, partial=True)
        job = Job(build=build, repository_id=build.repository_id, **data)
        if job.status != Status.queued and not job.date_started:
            job.date_started = timezone.now()

        job.date_updated = timezone.now()
        db.session.add(job)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return self.respond(status=422)

        celery.delay("zeus.aggregate_build_stats_for_job", job_id=job.id)

        return self.respond_with_schema(job_schema, job)
