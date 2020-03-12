from flask import current_app, request
from typing import List, Optional

from zeus.models import FileCoverage, Revision
from zeus.utils.builds import fetch_build_for_revision
from zeus.utils.trees import build_tree
from zeus.vcs import vcs_client

from .base_revision import BaseRevisionResource
from ..schemas import FileCoverageSchema

SEPERATOR = "/"

filecoverage_schema = FileCoverageSchema(many=False)


class RevisionFileCoverageTreeResource(BaseRevisionResource):
    def _get_leaf(self, revision: Revision, coverage_list: List[FileCoverage]):
        coverage = coverage_list[0]
        file_source: Optional[str] = None
        try:
            file_source = vcs_client.show(
                revision.repository_id, sha=revision.sha, filename=coverage.filename
            )
        except Exception:
            current_app.logger.exception(
                "Could not load file source for {} - {}",
                revision.sha,
                coverage.filename,
            )

        # TODO(dcramer): this needs to merge coverage nodes
        return {
            "is_leaf": True,
            "entries": [
                {
                    "name": coverage.filename,
                    "path": coverage.filename,
                    "lines_covered": coverage.lines_covered,
                    "lines_uncovered": coverage.lines_uncovered,
                    "diff_lines_covered": coverage.diff_lines_covered,
                    "diff_lines_uncovered": coverage.diff_lines_uncovered,
                    "is_leaf": True,
                }
            ],
            "coverage": filecoverage_schema.dump(coverage),
            "file_source": file_source,
        }

    def get(self, revision: Revision):
        """
        Return a tree of file coverage for the given revision.
        """
        build = fetch_build_for_revision(revision)
        if not build:
            return self.respond(status=404)

        parent = request.args.get("parent")

        build_ids = [original.id for original in build.original]

        query = FileCoverage.query.filter(
            FileCoverage.build_id.in_(build_ids)
        ).order_by(FileCoverage.filename.asc())

        if parent:
            query = query.filter(FileCoverage.filename.startswith(parent))

        coverage_list = list(query)

        is_leaf = all(c.filename == parent for c in coverage_list)

        if is_leaf:
            response = self._get_leaf(revision, coverage_list)
        elif coverage_list:
            groups = build_tree(
                list(set([f.filename for f in coverage_list])),
                sep=SEPERATOR,
                min_children=2,
                parent=parent,
            )

            results = []
            for group in groups:
                lines_covered, lines_uncovered = 0, 0
                diff_lines_covered, diff_lines_uncovered = 0, 0
                is_leaf = len(coverage_list) == 1 and coverage_list[0].filename == group
                for coverage in coverage_list:
                    if coverage.filename == group or coverage.filename.startswith(
                        group + SEPERATOR
                    ):
                        lines_covered += coverage.lines_covered
                        lines_uncovered += coverage.lines_uncovered
                        diff_lines_covered += coverage.diff_lines_covered
                        diff_lines_uncovered += coverage.diff_lines_uncovered

                if parent:
                    name = group[len(parent) + len(SEPERATOR) :]
                else:
                    name = group
                data = {
                    "name": name,
                    "path": group,
                    "lines_covered": lines_covered,
                    "lines_uncovered": lines_uncovered,
                    "diff_lines_covered": diff_lines_covered,
                    "diff_lines_uncovered": diff_lines_uncovered,
                    "is_leaf": is_leaf,
                }
                results.append(data)

            results.sort(key=lambda x: x["name"])
            response = {"is_leaf": False, "entries": results}
        else:
            response = {"is_leaf": False, "entries": []}

        trail = []
        context = []
        if parent:
            for chunk in parent.split(SEPERATOR):
                context.append(chunk)
                trail.append({"path": SEPERATOR.join(context), "name": chunk})

        response.update({"trail": trail})
        return response
