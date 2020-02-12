from flask import current_app, request

from zeus.constants import Result, Status
from zeus.models import Build, FileCoverage, Repository
from zeus.utils.trees import build_tree
from zeus.vcs import vcs_client

from .base_repository import BaseRepositoryResource
from ..schemas import FileCoverageSchema

SEPERATOR = "/"

filecoverage_schema = FileCoverageSchema(many=False)


class RepositoryFileCoverageTreeResource(BaseRepositoryResource):
    def _get_leaf(self, build: Build, coverage: FileCoverage):
        try:
            file_source = vcs_client.show(
                build.repository_id, sha=build.revision_sha, filename=coverage.filename
            )
        except Exception:
            file_source = None
            current_app.logger.exception(
                "Could not load file source for {} - {}",
                build.revision_sha,
                coverage.filename,
            )

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

    def get(self, repo: Repository):
        """
        Return a tree of coverage for the given revision.
        """
        build = (
            Build.query.filter(
                Build.repository_id == repo.id,
                Build.result == Result.passed,
                Build.status == Status.finished,
            )
            .order_by(Build.date_created.desc())
            .first()
        )

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
