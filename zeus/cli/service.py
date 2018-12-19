import click
import os
from flask import current_app

from .base import cli


@cli.group("service")
def service():
    pass


@service.command()
@click.option("--debug/--no-debug", default=False)
def scheduler(debug):
    os.environ["FLASK_DEBUG"] = "1" if debug else ""

    from zeus.config import queue, redis
    from zeus.queue.signals import worker_process_init

    worker_process_init.send(sender=queue)
    scheduler = queue.get_scheduler(connection=redis)
    for task_guid, task_config in current_app.config.get("CRON_SCHEDULE", {}).items():
        scheduler.schedule(guid=task_guid, repeat=True, **task_config)
    scheduler.run()


@service.command()
@click.option("--debug/--no-debug", default=False)
def worker(debug):
    os.environ["FLASK_DEBUG"] = "1" if debug else ""

    from zeus.config import queue
    from zeus.queue.signals import worker_process_init

    worker_process_init.send(sender=queue)
    queue.get_worker().listen()
