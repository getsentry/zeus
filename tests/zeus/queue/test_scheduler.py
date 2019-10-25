import pytest

from datetime import timedelta

from zeus.queue.scheduler import Scheduler


@pytest.fixture
def scheduler(sync_adapter, redis):
    return Scheduler(sync_adapter, redis)


def test_schedule_new_task(scheduler, redis):
    guid = "test_schedule_new_task"
    rv = scheduler.schedule(
        schedule=timedelta(minutes=1), task="example_task", guid=guid
    )
    assert rv

    task_key = scheduler.get_task_key(guid)
    config = redis.hgetall(task_key)
    assert config[b"kwargs"] == b"{}"
    assert config[b"args"] == b"[]"
    assert config[b"schedule"] == b"60.0"
    assert config[b"task"] == b"example_task"

    schedule_key = scheduler.get_schedule_key()
    items = redis.zrange(schedule_key, 0, -1)
    assert len(items) == 1
    assert items[0] == guid.encode("utf-8")
