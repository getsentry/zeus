from datetime import timedelta
from sqlalchemy.sql import func
from flask import current_app, request
from typing import List

from zeus.api.utils import stats
from zeus.config import db
from zeus.exceptions import UnknownRepositoryBackend
from zeus.models import Build, Repository, Revision
from zeus.utils import timezone

from .base_repository import BaseRepositoryResource


STAT_CHOICES = frozenset(
    (
        "builds.aborted",
        "builds.failed",
        "builds.passed",
        "builds.errored",
        "builds.total",
        "builds.duration",
        "tests.count",
        "tests.count_unique",
        "tests.duration",
        "coverage.lines_covered",
        "coverage.lines_uncovered",
        "coverage.diff_lines_covered",
        "coverage.diff_lines_uncovered",
        "style_violations.count",
        "bundle.total_asset_size",
    )
)


def get_revisions(repo: Repository, branch: str = None, limit: int = 200) -> List[str]:
    if current_app.config.get("MOCK_REVISIONS"):
        return (
            db.session.query(Revision.sha)
            .filter(Revision.repository_id == repo.id)
            .order_by(Revision.date_created.desc())
            .limit(limit)
            .all()
        )

    try:
        vcs = repo.get_vcs()
    except UnknownRepositoryBackend:
        return []

    if branch is None:
        branch = vcs.get_default_branch()

    return [r.sha for r in vcs.log(limit=limit, branch=branch, timeout=10)]


class RepositoryStatsResource(BaseRepositoryResource):
    def get(self, repo: Repository):
        """
        Return various stats per-day for the given repository.
        """
        stat = request.args.get("stat")
        if not stat:
            return self.error({"stat": "invalid stat"})

        if stat not in STAT_CHOICES:
            return self.error({"stat": "invalid stat"})

        aggregate = request.args.get("aggregate", "time")
        if aggregate not in ("time", "build"):
            return self.error({"aggregate": "invalid aggregate"})

        branch = request.args.get("branch")
        since = request.args.get("since")

        if since:
            date_end = timezone.fromtimestamp(float(since))
        else:
            date_end = timezone.now() + timedelta(days=1)

        date_end = date_end.replace(minute=0, second=0, microsecond=0)

        if aggregate == "time":
            resolution = request.args.get("resolution", "1d")
            points = int(request.args.get("points") or stats.POINTS_DEFAULT[resolution])
            if resolution == "1h":
                grouper = func.date_trunc("hour", Build.date_created)
                decr_res = stats.decr_hour
            elif resolution == "1d":
                grouper = func.date_trunc("day", Build.date_created)
                date_end = date_end.replace(hour=0)
                decr_res = stats.decr_day
            elif resolution == "1w":
                grouper = func.date_trunc("week", Build.date_created)
                date_end = date_end.replace(hour=0)
                date_end -= timedelta(days=date_end.weekday())
                decr_res = stats.decr_week
            elif resolution == "1m":
                grouper = func.date_trunc("month", Build.date_created)
                date_end = date_end.replace(hour=0, day=1)
                decr_res = stats.decr_month
        elif aggregate == "build":
            grouper = Build.number
            points = int(request.args.get("points") or 100)

        queryset = stats.build_queryset(stat, grouper, repo_id=repo.id)

        if aggregate == "time":
            date_begin = date_end
            for _ in range(points):
                date_begin = decr_res(date_begin)
            queryset = queryset.filter(
                Build.date_created >= date_begin, Build.date_created < date_end
            )
        elif aggregate == "build":
            revision_shas = get_revisions(repo, branch, limit=points * 2)
            queryset = queryset.filter(Build.revision_sha.in_(revision_shas)).order_by(
                Build.number.desc()
            )

        queryset = queryset.limit(points)

        if aggregate == "time":
            results = {
                # HACK(dcramer): force (but dont convert) the timezone to be utc
                # while this isnt correct, we're not looking for correctness yet
                k.replace(tzinfo=timezone.utc): v
                for k, v in queryset
            }

            data = []
            cur_date = date_end
            for _ in range(points):
                cur_date = decr_res(cur_date)
                data.append(
                    {
                        "time": int(float(cur_date.strftime("%s.%f")) * 1000),
                        "value": (
                            int(float(results[cur_date]))
                            if results.get(cur_date)
                            else (0 if stat in stats.ZERO_FILLERS else None)
                        ),
                    }
                )
        elif aggregate == "build":
            data = [
                {
                    "build": k,
                    "value": (
                        int(float(v))
                        if v is not None
                        else (0 if stat in stats.ZERO_FILLERS else None)
                    ),
                }
                for k, v in sorted(queryset, key=lambda x: -x[0])
            ]

        return self.respond(data)
