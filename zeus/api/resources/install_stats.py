from datetime import timedelta
from sqlalchemy.sql import func
from flask import request

from zeus.api.utils import stats
from zeus.config import db
from zeus.models import Build, User
from zeus.utils import timezone

from .base import Resource


STAT_CHOICES = frozenset(
    ("builds.errored", "builds.total", "users.active", "users.created")
)


class InstallStatsResource(Resource):
    def get(self):
        """
        Return various stats per-day for the installation.
        """
        stat = request.args.get("stat")
        if not stat:
            return self.error({"stat": "invalid stat"})

        if stat not in STAT_CHOICES:
            return self.error({"stat": "invalid stat"})

        since = request.args.get("since")

        if since:
            date_end = timezone.fromtimestamp(float(since))
        else:
            date_end = timezone.now() + timedelta(days=1)

        if stat == "users.active":
            date_field = User.date_active
        elif stat == "users.created":
            date_field = User.date_created
        else:
            date_field = Build.date_created

        date_end = date_end.replace(minute=0, second=0, microsecond=0)

        resolution = request.args.get("resolution", "1d")
        points = int(request.args.get("points") or stats.POINTS_DEFAULT[resolution])
        if resolution == "1h":
            grouper = func.date_trunc("hour", date_field)
            decr_res = stats.decr_hour
        elif resolution == "1d":
            grouper = func.date_trunc("day", date_field)
            date_end = date_end.replace(hour=0)
            decr_res = stats.decr_day
        elif resolution == "1w":
            grouper = func.date_trunc("week", date_field)
            date_end = date_end.replace(hour=0)
            date_end -= timedelta(days=date_end.weekday())
            decr_res = stats.decr_week
        elif resolution == "1m":
            grouper = func.date_trunc("month", date_field)
            date_end = date_end.replace(hour=0, day=1)
            decr_res = stats.decr_month

        date_begin = date_end
        for _ in range(points):
            date_begin = decr_res(date_begin)

        if stat.startswith("users."):
            queryset = db.session.query(
                grouper.label("grouper"), func.count(User.id)
            ).group_by("grouper")
        else:
            queryset = stats.build_queryset(stat, grouper)

        queryset = queryset.filter(date_field >= date_begin, date_field < date_end)

        queryset = queryset.limit(points)

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

        return self.respond(data)
