from flask import request
from operator import or_

from zeus.models import FileCoverage, Revision
from zeus.utils.builds import fetch_build_for_revision

from .base_revision import BaseRevisionResource
from ..schemas import FileCoverageSchema

filecoverage_schema = FileCoverageSchema(many=True, strict=True)


class RevisionFileCoverageResource(BaseRevisionResource):
    def get(self, revision: Revision):
        """
        Return a list of file coverage objects for a given revision.
        """
        build = fetch_build_for_revision(revision.repository, revision)
        build_ids = [original.id for original in build.original]
        query = FileCoverage.query.filter(
            FileCoverage.build_id.in_(build_ids),
        )

        diff_only = request.args.get('diff_only') in ('1', 'yes', 'true')
        if diff_only:
            query = query.filter(
                or_(FileCoverage.diff_lines_covered > 0,
                    FileCoverage.diff_lines_uncovered > 0)
            )

        query = query.order_by(
            (FileCoverage.diff_lines_covered +
             FileCoverage.diff_lines_uncovered > 0).desc(),
            FileCoverage.filename.asc()
        )

        return self.respond_with_schema(filecoverage_schema, query)
