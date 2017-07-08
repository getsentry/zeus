from zeus.models import Job

from .base import Resource
from ..schemas import JobSchema

job_schema = JobSchema(strict=True)


class JobDetailsResource(Resource):
    def get(self, job_id):
        """
        Return a job.
        """
        job = Job.query.get(job_id)
        if not job:
            return self.not_found()
        return self.respond_with_schema(job_schema, job)
