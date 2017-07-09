from zeus.config import db
from zeus.constants import Status
from zeus.models import Job
from zeus.tasks import aggregate_build_stats_for_job

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
        data = result.data
        if data.get('status'):
            job.status = data['status']
        if data.get('result'):
            job.result = data['result']
        if db.session.is_modified(job):
            db.session.add(job)
            db.session.commit()

        if job.status == Status.finished:
            aggregate_build_stats_for_job.delay(job_id=job.id)

        return self.respond_with_schema(job_schema, job)
