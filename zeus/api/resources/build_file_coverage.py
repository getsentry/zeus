from flask import request
from operator import or_
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

        diff_only = request.args.get('diff_only') in ('1', 'yes', 'true')
        if diff_only:
            query = query.filter(
                or_(FileCoverage.diff_lines_covered > 0, FileCoverage.diff_lines_uncovered > 0)
            )

        return self.respond_with_schema(filecoverage_schema, query)
