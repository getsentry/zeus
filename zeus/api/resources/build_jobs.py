from __future__ import absolute_import, division, unicode_literals

from zeus.models import Build, Job

from .base import Resource
from ..schemas import JobSchema

jobs_schema = JobSchema(many=True, strict=True)


class BuildJobsResource(Resource):
    def get(self, build_id):
        """
        Return a list of jobs for a given build.
        """
        build = Build.query.get(build_id)
        if not build:
            return self.not_found()

        query = Job.query.filter(Job.build_id == build.id)
        return jobs_schema.dump(query).data
