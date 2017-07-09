from zeus.models import Build, Job

from .base_build import BaseBuildResource
from ..schemas import JobSchema

jobs_schema = JobSchema(many=True, strict=True)


class BuildJobsResource(BaseBuildResource):
    def get(self, build: Build):
        """
        Return a list of jobs for a given build.
        """
        query = Job.query.filter(Job.build_id == build.id).order_by(Job.number.asc())
        return self.respond_with_schema(jobs_schema, query)
