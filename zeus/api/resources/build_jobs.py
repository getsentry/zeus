from zeus.models import Build, Job, Repository

from .base import Resource
from ..schemas import JobSchema

jobs_schema = JobSchema(many=True, strict=True)


class BuildJobsResource(Resource):
    def get(self, repository_name: str, build_number: int):
        """
        Return a list of jobs for a given build.
        """
        build = Build.query.join(Repository, Repository.id == Build.repository_id).filter(
            Repository.name == repository_name,
            Build.number == build_number,
        ).first()
        if not build:
            return self.not_found()

        query = Job.query.filter(Job.build_id == build.id).order_by(Job.number.asc())
        return self.respond_with_schema(jobs_schema, query)
