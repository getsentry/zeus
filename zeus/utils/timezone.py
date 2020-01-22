# this module implements an interface similar to django.utils.timezone
from datetime import datetime, timezone

utc = timezone.utc


def now(tzinfo=timezone.utc):
    return datetime.now(tzinfo)


def fromtimestamp(ts, tzinfo=timezone.utc):
    return datetime.utcfromtimestamp(ts).replace(tzinfo=tzinfo)
