from flask import request
from operator import or_

from zeus.models import Build, FileCoverage

from .base_build import BaseBuildResource
from ..schemas import FileCoverageSchema

filecoverage_schema = FileCoverageSchema(many=True, strict=True)


class BuildFileCoverageResource(BaseBuildResource):
    def get(self, build: Build):
        """
        Return a list of file coverage objects for a given build.
        """
        query = FileCoverage.query.filter(FileCoverage.build_id == build.id)

        diff_only = request.args.get("diff_only") in ("1", "yes", "true")
        if diff_only:
            query = query.filter(
                or_(
                    FileCoverage.diff_lines_covered > 0,
                    FileCoverage.diff_lines_uncovered > 0,
                )
            )

        query = query.order_by(
            (
                FileCoverage.diff_lines_covered + FileCoverage.diff_lines_uncovered > 0
            ).desc(),
            FileCoverage.filename.asc(),
        )

        return self.respond_with_schema(filecoverage_schema, query)
