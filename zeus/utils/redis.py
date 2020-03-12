import time
from contextlib import contextmanager
from random import random

import redis


class UnableToGetLock(Exception):
    pass


class Redis(object):
    UnableToGetLock = UnableToGetLock

    def __init__(self, app=None):
        self.redis = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.redis = redis.from_url(app.config["REDIS_URL"])
        self.logger = app.logger

    def __getattr__(self, name):
        return getattr(self.redis, name)

    @contextmanager
    def lock(
        self,
        lock_key: str,
        timeout: float = 3.0,
        expire: int = None,
        nowait: bool = False,
    ):
        """
        Context manager for using a redis lock with the given key

        Arguments:
            lock_key (string): key to lock
            timeout (float): how long (in seconds) to try locking.
                             An exception is raised if the lock can't be acquired.
            expire (float): how long (in seconds) we can hold lock before it is
                            automatically released
            nowait (bool): if True, don't block if can't acquire the lock
                           (will instead raise an exception)
        """

        conn = self.redis

        if expire is None:
            expire = timeout

        delay = 0.01 + random() / 10
        lock = conn.lock(lock_key, timeout=expire, sleep=delay)

        self.logger.info("Acquiring lock on %s", lock_key)
        acquired = lock.acquire(blocking=not nowait, blocking_timeout=timeout)
        start = time.time()

        if not acquired:
            raise self.UnableToGetLock("Unable to fetch lock on %s" % (lock_key,))

        self.logger.info("Successfully acquired lock on %s", lock_key)

        try:
            yield

        finally:
            self.logger.info("Releasing lock on %s", lock_key)

            try:
                lock.release()
            except Exception:
                self.logger.exception(
                    "Error releasing lock on %s, acquired around %.2f s ago",
                    lock_key,
                    time.time() - start,
                )

    def incr(self, key: str):
        self.redis.incr(key)

    def decr(self, key: str):
        self.redis.decr(key)
