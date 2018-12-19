from zeus.queue.task import Task


def test_call_task_passthru(example_task):
    task = Task(func=example_task)
    assert task("hola") == "hola"


def test_task_implicit_name(example_task):
    task = Task(func=example_task)
    assert task.name == "conftest.example_task_"


def test_task_explicit_name(example_task):
    task = Task(func=example_task, name="test-task")
    assert task.name == "test-task"
