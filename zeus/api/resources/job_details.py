from zeus.models import Build, Job, Repository

from .base import Resource
from ..schemas import JobSchema

job_schema = JobSchema(strict=True)


class JobDetailsResource(Resource):
    def get(self, repository_name: str, build_number: int, job_number: int):
        """
        Return a job.
        """
        job = Job.query.join(Build, Build.id == Job.build_id).join(
            Repository, Repository.id == Build.repository_id
        ).filter(
            Repository.name == repository_name,
            Build.number == build_number,
            Job.number == job_number,
        ).first()
        if not job:
            return self.not_found()
        return self.respond_with_schema(job_schema, job)
