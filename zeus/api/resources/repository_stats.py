from datetime import datetime, timedelta
from flask import current_app, request
from sqlalchemy.sql import extract, func
from typing import List
from uuid import UUID

from zeus.config import db
from zeus.exceptions import UnknownRepositoryBackend
from zeus.models import Build, ItemStat, Repository, Result, Source, Status
from zeus.utils import timezone

from .base_repository import BaseRepositoryResource


STAT_CHOICES = frozenset(
    (
        "builds.aborted",
        "builds.failed",
        "builds.passed",
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

ZERO_FILLERS = frozenset(
    ("builds.total", "tests.count", "tests.count_unique", "style_violations.count")
)

RESOLUTION_CHOICES = ("1h", "1d", "1w", "1m")

AGG_CHOICES = ("sum", "avg")

POINTS_DEFAULT = {"1h": 24, "1d": 30, "1w": 26, "1m": 12}


def decr_month(dt: datetime) -> datetime:
    if dt.month == 1:
        return dt.replace(month=12, year=dt.year - 1)

    return dt.replace(month=dt.month - 1)


def decr_week(dt: datetime) -> datetime:
    return dt - timedelta(days=7)


def decr_hour(dt: datetime) -> datetime:
    return dt - timedelta(hours=1)


def decr_day(dt: datetime) -> datetime:
    return dt - timedelta(days=1)


def build_queryset(repo_id: UUID, stat: str, grouper):
    # TODO(dcramer): put minimum date bounds
    if stat in (
        "builds.aborted",
        "builds.failed",
        "builds.passed",
        "builds.total",
        "builds.duration",
    ):
        if stat == "builds.failed":
            extra_filters = [Build.result == Result.failed]
        elif stat == "builds.passed":
            extra_filters = [Build.result == Result.passed]
        elif stat == "builds.aborted":
            extra_filters = [Build.result == Result.aborted]
        else:
            extra_filters = [Build.status == Status.finished]

        if stat == "builds.duration":
            value = func.avg(
                (
                    extract("epoch", Build.date_finished)
                    - extract("epoch", Build.date_started)
                )
                * 1000
            )
            extra_filters.append(Build.result == Result.passed)
        else:
            value = func.count(Build.id)

        queryset = (
            db.session.query(grouper.label("grouper"), value.label("value"))
            .filter(Build.repository_id == repo_id, *extra_filters)
            .group_by("grouper")
        )
    else:
        queryset = (
            db.session.query(
                grouper.label("grouper"), func.avg(ItemStat.value).label("value")
            )
            .filter(
                ItemStat.item_id == Build.id,
                ItemStat.name == stat,
                Build.repository_id == repo_id,
                Build.result == Result.passed,
            )
            .group_by("grouper")
        )

    return queryset


def get_revisions(repo: Repository, branch: str = None, limit: int = 200) -> List[str]:
    if current_app.config.get("MOCK_REVISIONS"):
        return (
            db.session.query(Source.revision_sha)
            .filter(Source.repository_id == repo.id)
            .order_by(Source.date_created.desc())
            .limit(limit)
            .all()
        )

    try:
        vcs = repo.get_vcs()
    except UnknownRepositoryBackend:
        return []

    if branch is None:
        branch = vcs.get_default_branch()

    return [r.sha for r in vcs.log(limit=limit, branch=branch)]


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
            date_end = datetime.utcfromtimestamp(float(since)).replace(
                tzinfo=timezone.utc
            )
        else:
            date_end = timezone.now() + timedelta(days=1)

        date_end = date_end.replace(minute=0, second=0, microsecond=0)

        if aggregate == "time":
            resolution = request.args.get("resolution", "1d")
            points = int(request.args.get("points") or POINTS_DEFAULT[resolution])
            if resolution == "1h":
                grouper = func.date_trunc("hour", Build.date_created)
                decr_res = decr_hour
            elif resolution == "1d":
                grouper = func.date_trunc("day", Build.date_created)
                date_end = date_end.replace(hour=0)
                decr_res = decr_day
            elif resolution == "1w":
                grouper = func.date_trunc("week", Build.date_created)
                date_end = date_end.replace(hour=0)
                date_end -= timedelta(days=date_end.weekday())
                decr_res = decr_week
            elif resolution == "1m":
                grouper = func.date_trunc("month", Build.date_created)
                date_end = date_end.replace(hour=0, day=1)
                decr_res = decr_month
        elif aggregate == "build":
            grouper = Build.number
            points = int(request.args.get("points") or 100)

        queryset = build_queryset(repo.id, stat, grouper)

        if aggregate == "time":
            date_begin = date_end
            for _ in range(points):
                date_begin = decr_res(date_begin)
            queryset = queryset.filter(
                Build.date_created >= date_begin, Build.date_created < date_end
            )
        elif aggregate == "build":
            revision_shas = get_revisions(repo, branch, limit=points * 2)
            queryset = (
                queryset.join(Source, Source.id == Build.source_id)
                .filter(Source.revision_sha.in_(revision_shas))
                .order_by(Build.number.desc())
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
                            else (0 if stat in ZERO_FILLERS else None)
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
                        else (0 if stat in ZERO_FILLERS else None)
                    ),
                }
                for k, v in sorted(queryset, key=lambda x: -x[0])
            ]

        return self.respond(data)
