import asyncio

from contextlib import contextmanager
from functools import wraps
from sentry_sdk import Hub
from sentry_sdk.tracing import Span as SentrySpan
from typing import Callable, Generator, overload


# https://stackoverflow.com/questions/44169998/how-to-create-a-python-decorator-that-can-wrap-either-coroutine-or-function


@contextmanager
def Span(op: str, description: str = None) -> Generator[SentrySpan, None, None]:
    with Hub.current.start_span(op=op, description=description) as span:
        yield span


@overload
def span(op: str, desc_or_func: str = None) -> Callable:
    pass


@overload
def span(op: str, desc_or_func: Callable = None) -> Callable:
    pass


def span(op: str, desc_or_func=None) -> Callable:
    def inner(func):
        @contextmanager
        def wrap_with_span(args, kwargs):
            if callable(desc_or_func):
                description = desc_or_func(*args, **kwargs)
            else:
                description = desc_or_func
            with Hub.current.start_span(op=op, description=description):
                yield

        @wraps(func)
        def wrapper(*args, **kwargs):
            if not asyncio.iscoroutinefunction(func):
                with wrap_with_span(args, kwargs):
                    return func(*args, **kwargs)
            else:

                async def tmp():
                    with wrap_with_span(args, kwargs):
                        return await func(*args, **kwargs)

                return tmp()

        return wrapper

    return inner
