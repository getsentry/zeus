from flask import request

from zeus.models import Build, FileCoverage
from zeus.utils.trees import build_tree

from .base_build import BaseBuildResource

SEPERATOR = '/'


class BuildFileCoverageTreeResource(BaseBuildResource):
    def get(self, build: Build):
        """
        Return a tree of coverage for the given build.
        """
        parent = request.args.get('parent')

        query = FileCoverage.query.filter(
            FileCoverage.build_id == build.id,
        ).order_by(
            FileCoverage.filename.asc()
        )
        if parent:
            query = query.filter(
                FileCoverage.filename.startswith(parent),
            )

        coverage_list = list(query)

        if coverage_list:
            groups = build_tree(
                [f.filename for f in coverage_list],
                sep=SEPERATOR,
                min_children=2,
                parent=parent,
            )

            results = []
            for group in groups:
                lines_covered, lines_uncovered = 0, 0
                for coverage in coverage_list:
                    if coverage.filename == group or coverage.filename.startswith(
                            group + SEPERATOR):
                        lines_covered += coverage.lines_covered
                        lines_uncovered += coverage.lines_uncovered

                if parent:
                    name = group[len(parent) + len(SEPERATOR):]
                else:
                    name = group
                data = {
                    'name': name,
                    'path': group,
                    'lines_covered': lines_covered,
                    'lines_uncovered': lines_uncovered,
                }
                results.append(data)

            results.sort(key=lambda x: x['name'])

            trail = []
            context = []
            if parent:
                for chunk in parent.split(SEPERATOR):
                    context.append(chunk)
                    trail.append({
                        'path': SEPERATOR.join(context),
                        'name': chunk,
                    })
        else:
            results = []
            trail = []

        return {
            'entries': results,
            'trail': trail,
        }
