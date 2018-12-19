import pytest

from zeus.queue.adapters.sync import SyncAdapter
from zeus.queue.task import Task


def example_task_(req, opt=None):
    if req == "error":
        raise Exception
    return req


@pytest.fixture
def example_task():
    return example_task_


@pytest.fixture
def task_registry(example_task):
    return {"example_task": Task(func=example_task)}


@pytest.fixture
def sync_adapter(task_registry):
    return SyncAdapter(task_registry=task_registry)
