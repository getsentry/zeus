import calendar
import json
import redis

from datetime import datetime, timedelta
from flask import current_app
from time import sleep
from typing import List, Optional, Mapping

from zeus.utils import timezone


def from_unix(float) -> datetime:
    return datetime.utcfromtimestamp(float).replace(tzinfo=timezone.utc)


def to_unix(dt) -> float:
    return calendar.timegm(dt.utctimetuple())


class Scheduler(object):
    """
    Uses a sorted set in Redis to keep track of scheduled tasks.

    The key is the task name (as registered in the system), and the score is
    the unix timestamp for the earliest time the task should run.
    """

    def __init__(
        self,
        adapter,
        connection: redis.Redis,
        scheduled_tasks_prefix: str = "scheduler",
    ):
        self.adapter = adapter
        self.connection = connection
        self.scheduled_tasks_prefix = scheduled_tasks_prefix

    def get_schedule_key(self):
        return "{}:schedule".format(self.scheduled_tasks_prefix)

    def get_task_key(self, guid):
        return "{}:task:{}".format(self.scheduled_tasks_prefix, guid)

    def schedule(
        self,
        schedule: timedelta,
        task: str,
        guid: str = None,
        repeat: bool = False,
        args: Optional[List] = None,
        kwargs: Optional[Mapping] = None,
    ) -> bool:
        """
        Schedule a task to be run periodically at ``schedule``.

        If ``guid`` is already present in the scheduler, this will simply update
        the config for the task, but not adjust the next-run time unless the interval
        has changed.

        Return bool representing if the task's schedule was adjusted.
        """
        if not guid:
            guid = task

        task_key = self.get_task_key(guid)
        total_seconds = schedule.total_seconds()
        target_timestamp = to_unix(timezone.now() + schedule)

        pipe = self.connection.pipeline()
        pipe.hgetall(task_key)
        pipe.hmset(
            task_key,
            {
                "task": task,
                "schedule": total_seconds,
                "repeat": int(repeat),
                "args": json.dumps(list(args) if args else []),
                "kwargs": json.dumps(dict(kwargs) if kwargs else {}),
            },
        )
        # we set an expiration just to avoid any GC concerns due to failures
        pipe.expireat(task_key, int(target_timestamp + total_seconds))
        prev_config = pipe.execute()[0]

        schedule_key = self.get_schedule_key()
        pipe = self.connection.pipeline()

        # this could be smarter on the "dont update" check, and simply update
        # if its beyond current schedules target_timestamp
        pipe.zadd(
            schedule_key,
            {guid: target_timestamp},
            # 'dont update' only if the schedule is identical
            xx=int(prev_config.get("schedule", 0)) == total_seconds,
        )
        pipe.zscore(schedule_key, guid)
        rv, scheduled_timestamp = pipe.execute()

        current_app.logger.info(
            "Scheduled job %s [task: %s] to run every %ss [eta: %s]",
            guid,
            task,
            total_seconds,
            from_unix(scheduled_timestamp),
        )
        return rv > 0

    def enqueue_tasks(self) -> int:
        """
        Schedule any tasks which have hit their target run time.

        Return the number of scheduled tasks.
        """
        schedule_key = self.get_schedule_key()

        current_app.logger.debug("Checking for scheduled tasks")
        until = to_unix(timezone.now())
        pending_tasks = self.connection.zrangebyscore(schedule_key, 0, until)
        n = 0
        for task_guid in (t.decode("utf-8") for t in pending_tasks):
            n += 1
            task_key = self.get_task_key(task_guid)
            # sigh
            config = {
                k.decode("utf-8"): v.decode("utf-8")
                for k, v in self.connection.hgetall(task_key).items()
            }
            if not config:
                current_app.logger.error(
                    "Missing scheduled task configuration for %s", task_guid
                )
                self.connection.zrek(schedule_key, task_guid)
                continue

            task_name = config["task"]
            current_app.logger.info("Enqueuing job %s [task: %s]", task_guid, task_name)
            self.adapter.enqueue(
                task_name, kwargs=json.loads(config.get("kwargs") or "{}")
            )

            schedule = float(config["schedule"])
            target_timestamp = to_unix(timezone.now()) + schedule
            pipe = self.connection.pipeline()
            if int(config.get("repeat", "0")):
                pipe.zadd(schedule_key, {task_guid: target_timestamp})
                pipe.expireat(task_key, int(target_timestamp + schedule))
            else:
                pipe.zrem(schedule_key, task_guid)
                pipe.delete(task_key)
            pipe.execute()
        return n

    def run(self):
        """
        Run continuously pushing tasks into the queue per their schedule.
        """
        current_app.logger.info("Scheduler is running")
        while True:
            try:
                self.enqueue_tasks()
                sleep(10)
            except KeyboardInterrupt:
                break
