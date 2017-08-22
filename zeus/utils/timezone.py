# this module implements an interface similar to django.utils.timezone
from datetime import datetime, timezone

utc = timezone.utc


def now():
    return datetime.now(timezone.utc)
