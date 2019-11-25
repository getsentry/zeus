from flask import request

from zeus.models import Build, FileCoverage
from zeus.utils.trees import build_tree

from .base_build import BaseBuildResource
from ..schemas import FileCoverageSchema

SEPERATOR = "/"

filecoverage_schema = FileCoverageSchema(many=False)


class BuildFileCoverageTreeResource(BaseBuildResource):
    def _get_leaf(self, build: Build, coverage: FileCoverage):
        file_source = None
        vcs = build.repository.get_vcs()
        if vcs:
            try:
                file_source = vcs.show(build.revision_sha, coverage.filename)
            except Exception:
                pass

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

    def get(self, build: Build):
        """
        Return a tree of coverage for the given build.
        """
        parent = request.args.get("parent")

        query = FileCoverage.query.filter(FileCoverage.build_id == build.id).order_by(
            FileCoverage.filename.asc()
        )
        if parent:
            query = query.filter(FileCoverage.filename.startswith(parent))

        coverage_list = list(query)

        is_leaf = len(coverage_list) == 1 and coverage_list[0].filename == parent

        if is_leaf:
            response = self._get_leaf(build, coverage_list[0])
        elif coverage_list:
            groups = build_tree(
                [f.filename for f in coverage_list],
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
