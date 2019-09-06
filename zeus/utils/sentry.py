from functools import wraps
from sentry_sdk import Hub


def span(op, desc_or_func=None):
    def inner(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if callable(desc_or_func):
                description = desc_or_func(*args, **kwargs)
            else:
                description = desc_or_func
            with Hub.current.start_span(op=op, description=description):
                return func(*args, **kwargs)

        return wrapped

    return inner
