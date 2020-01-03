import click

from zeus.tasks import (
    cleanup_artifacts,
    cleanup_builds,
    cleanup_build_refs,
    cleanup_build_stats,
    cleanup_jobs,
    cleanup_pending_artifacts,
)

from .base import cli


@cli.group("cleanup")
def cleanup():
    pass


@cleanup.command()
@click.option("--task-limit", type=int, default=1000)
def builds(task_limit: int):
    cleanup_builds(task_limit=task_limit)


@cleanup.command()
@click.option("--task-limit", type=int, default=1000)
def build_refs(task_limit: int):
    cleanup_build_refs(task_limit)


@cleanup.command()
@click.option("--task-limit", type=int, default=1000)
def build_stats(task_limit: int):
    cleanup_build_stats(task_limit)


@cleanup.command()
@click.option("--task-limit", type=int, default=1000)
def jobs(task_limit: int):
    cleanup_jobs(task_limit)


@cleanup.command()
@click.option("--task-limit", type=int, default=1000)
def artifacts(task_limit: int):
    cleanup_artifacts(task_limit)


@cleanup.command()
@click.option("--task-limit", type=int, default=1000)
def pending_artifacts(task_limit: int):
    cleanup_pending_artifacts(task_limit)
