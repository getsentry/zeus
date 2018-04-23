from datetime import datetime, timedelta
from flask import request
from sqlalchemy.sql import extract, func

from zeus.config import db
from zeus.models import Build, ItemStat, Repository, Result, Status
from zeus.utils import timezone

from .base_repository import BaseRepositoryResource


STAT_CHOICES = (
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

RESOLUTION_CHOICES = ("1h", "1d", "1w", "1m")

AGG_CHOICES = ("sum", "avg")

POINTS_DEFAULT = {"1h": 24, "1d": 30, "1w": 26, "1m": 12}


def decr_month(dt):
    if dt.month == 1:
        return dt.replace(month=12, year=dt.year - 1)

    return dt.replace(month=dt.month - 1)


def decr_week(dt):
    return dt - timedelta(days=7)


def decr_hour(dt):
    return dt - timedelta(hours=1)


def decr_day(dt):
    return dt - timedelta(days=1)


class RepositoryStatsResource(BaseRepositoryResource):

    def get(self, repo: Repository):
        """
        Return various stats per-day for the given repository.
        """
        stat = request.args.get("stat")
        if not stat:
            return self.error("missing stat")

        if stat not in STAT_CHOICES:
            return self.error("invalid stat")

        resolution = request.args.get("resolution", "1d")
        points = int(request.args.get("points") or POINTS_DEFAULT[resolution])
        since = request.args.get("since")

        if since:
            date_end = datetime.utcfromtimestamp(float(since)).replace(
                tzinfo=timezone.utc
            )
        else:
            date_end = timezone.now()

        date_end = date_end.replace(minute=0, second=0, microsecond=0)

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

        date_begin = date_end
        for _ in range(points):
            date_begin = decr_res(date_begin)

        # TODO(dcramer): put minimum date bounds
        if stat in (
            "builds.aborted",
            "builds.failed",
            "builds.passed",
            "builds.total",
            "builds.duration",
        ):
            if stat == "builds.failed":
                filters = [Build.result == Result.failed]
            elif stat == "builds.passed":
                filters = [Build.result == Result.passed]
            elif stat == "builds.aborted":
                filters = [Build.result == Result.aborted]
            else:
                filters = [Build.status == Status.finished]

            if stat == "builds.duration":
                value = func.avg(
                    (
                        extract("epoch", Build.date_finished)
                        - extract("epoch", Build.date_started)
                    )
                    * 1000
                )
                filters = [
                    Build.status == Status.finished, Build.result == Result.passed
                ]
            else:
                value = func.count(Build.id)

            results = {
                # HACK(dcramer): force (but dont convert) the timezone to be utc
                # while this isnt correct, we're not looking for correctness yet
                k.replace(tzinfo=timezone.utc): v
                for k, v in db.session.query(
                    grouper.label("grouper"), value.label("value")
                ).filter(
                    Build.repository_id == repo.id,
                    Build.date_created >= date_begin,
                    Build.date_created < date_end,
                    *filters
                ).group_by(
                    "grouper"
                )
            }
        else:
            results = {
                # HACK(dcramer): force (but dont convert) the timezone to be utc
                # while this isnt correct, we're not looking for correctness yet
                k.replace(tzinfo=timezone.utc): v
                for k, v in db.session.query(
                    grouper.label("grouper"), func.avg(ItemStat.value).label("value")
                ).filter(
                    ItemStat.item_id == Build.id,
                    ItemStat.name == stat,
                    Build.repository_id == repo.id,
                    Build.result == Result.passed,
                    Build.date_created >= date_begin,
                    Build.date_created < date_end,
                ).group_by(
                    "grouper"
                )
            }

        data = []
        cur_date = date_end
        for _ in range(points):
            cur_date = decr_res(cur_date)
            data.append(
                {
                    "time": int(float(cur_date.strftime("%s.%f")) * 1000),
                    "value": int(float(results.get(cur_date) or 0)),
                }
            )
        # data.reverse()

        return self.respond(data)
