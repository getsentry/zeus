from zeus.config import db
from zeus.constants import Status
from zeus.models import Job
from zeus.tasks import aggregate_build_stats_for_job
from zeus.utils import timezone

from .base_job import BaseJobResource
from ..schemas import JobSchema

job_schema = JobSchema(strict=True)


class JobDetailsResource(BaseJobResource):
    def get(self, job: Job):
        """
        Return a job.
        """
        return self.respond_with_schema(job_schema, job)

    def put(self, job: Job):
        """
        Update a job.
        """
        result = self.schema_from_request(job_schema, partial=True)
        if result.errors:
            return self.respond(result.errors, 403)

        was_unfinished = job.status != Status.finished

        for key, value in result.data.items():
            if getattr(job, key) != value:
                setattr(job, key, value)

        if db.session.is_modified(job):
            if job.status == Status.finished and was_unfinished and not job.date_finished:
                job.date_finished = timezone.now()
            db.session.add(job)
            db.session.commit()

            aggregate_build_stats_for_job.delay(job_id=job.id)

        return self.respond_with_schema(job_schema, job)
