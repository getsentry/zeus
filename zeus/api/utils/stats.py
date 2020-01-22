from datetime import datetime, timedelta
from sqlalchemy.sql import extract, func
from uuid import UUID

from zeus.config import db
from zeus.constants import Result, Status
from zeus.models import Build, ItemStat

ZERO_FILLERS = frozenset(
    (
        "builds.total",
        "builds.errored",
        "builds.passed",
        "builds.failed",
        "builds.aborted",
        "tests.count",
        "tests.count_unique",
        "style_violations.count",
        "users.active",
        "users.created",
    )
)

RESOLUTION_CHOICES = frozenset(("1h", "1d", "1w", "1m"))

AGG_CHOICES = frozenset(("sum", "avg"))

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


def build_queryset(stat: str, grouper, repo_id: UUID = None):
    # TODO(dcramer): put minimum date bounds
    if stat in (
        "builds.aborted",
        "builds.failed",
        "builds.passed",
        "builds.errored",
        "builds.total",
        "builds.duration",
    ):
        if stat == "builds.failed":
            extra_filters = [Build.result == Result.failed]
        elif stat == "builds.passed":
            extra_filters = [Build.result == Result.passed]
        elif stat == "builds.aborted":
            extra_filters = [Build.result == Result.aborted]
        elif stat == "builds.errored":
            extra_filters = [Build.result == Result.errored]
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
            .filter(*extra_filters)
            .group_by("grouper")
        )
        if repo_id:
            queryset = queryset.filter(Build.repository_id == repo_id)
    else:
        queryset = (
            db.session.query(
                grouper.label("grouper"), func.avg(ItemStat.value).label("value")
            )
            .filter(
                ItemStat.item_id == Build.id,
                ItemStat.name == stat,
                Build.result == Result.passed,
            )
            .group_by("grouper")
        )
        if repo_id:
            queryset = queryset.filter(Build.repository_id == repo_id)

    return queryset
