from sqlalchemy.orm import contains_eager

from zeus.models import Build, FileCoverage, Job

from .base_build import BaseBuildResource
from ..schemas import FileCoverageSchema

filecoverage_schema = FileCoverageSchema(many=True, strict=True)


class BuildFileCoverageResource(BaseBuildResource):
    def get(self, build: Build):
        """
        Return a list of file coverage objects for a given build.
        """
        query = FileCoverage.query.options(contains_eager('job')).join(
            Job,
            FileCoverage.job_id == Job.id,
        ).filter(
            Job.build_id == build.id,
        )

        return self.respond_with_schema(filecoverage_schema, query)
