from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc)
