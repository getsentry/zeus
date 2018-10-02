from array import array
from contextlib import contextmanager
from flask import current_app, request
from time import time
from uuid import uuid4


class HitCounter(object):
    def __init__(self, size: int = 3600):
        self.size = size
        self.reset()

    def reset(self):
        self.buffer = array("l", [0] * self.size)
        self.ts = 0

    def trim(self, new_ts):
        last_ts = self.ts
        if not last_ts:
            return

        delta = new_ts - last_ts
        if not delta:
            return

        size = self.size
        if delta > self.size:
            self.reset()
        else:
            for i in range(1, delta + 1):
                self.buffer[(last_ts + i) % size] = 0

    def incr(self, current_ts: float = None):
        new_ts = int(current_ts or time())
        self.trim(new_ts)
        self.buffer[new_ts % self.size] += 1
        self.ts = new_ts

    def count(self, seconds: int = None, current_ts: float = None) -> int:
        size = self.size
        last_ts = self.ts
        if seconds is None:
            seconds = size

        assert seconds <= size
        current_ts = int(current_ts or time())

        delta = current_ts - last_ts
        if delta >= size:
            return 0

        result = 0
        for i in range(delta, seconds):
            result += self.buffer[(current_ts - i) % size]
        return result


class Counter(object):
    def __init__(self, value: int = 0):
        self.value = value

    def incr(self, amount: int = 1):
        self.value += amount

    def decr(self, amount: int = 1):
        self.value -= amount


@contextmanager
def gauge(counter):
    counter.incr()
    yield
    counter.decr()


class MetricsExtension(object):
    def __init__(self, size: int):
        self.hits = HitCounter(size=size)
        self.connections = Counter()
        self.started = time()
        self.guid = uuid4()

    @property
    def uptime(self) -> float:
        return time() - self.started


class Metrics(object):
    def __init__(self, size: int = 3600):
        self.size = size

    def init_app(self, app):
        metrics = MetricsExtension(self.size)

        @app.before_request
        def metrics_before_request():
            connections_gauge = gauge(metrics.connections)
            request.connections_gauge = connections_gauge
            connections_gauge.__enter__()
            metrics.hits.incr()

        @app.after_request
        def metrics_after_request(response):
            try:
                request.connections_gauge.__exit__(None, None, None)
            except Exception:
                pass
            return response

        app.extensions["metrics"] = metrics

    def __getattr__(self, attr):
        return getattr(current_app.extensions["metrics"], attr)
