import click
import os
import subprocess
import sys

from .base import cli


@cli.command()
@click.option("--log-level", "-l", default="INFO")
@click.option("--cron/--no-cron", default=True)
def worker(cron, log_level):
    command = [
        "celery",
        "--app=zeus.app:celery",
        "worker",
        "--loglevel={}".format(log_level),
        # TODO(dcramer): which of these can we kill?
        # '--without-mingle',
        # '--without-gossip',
        # '--without-heartbeat',
        "--max-tasks-per-child=10000",
    ]
    if cron:
        command.extend(["--beat", "--scheduler=redbeat.RedBeatScheduler"])

    sys.exit(
        subprocess.call(
            command,
            cwd=os.getcwd(),
            env=os.environ,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    )
