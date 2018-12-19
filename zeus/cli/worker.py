import click
import multiprocessing
import os
import sys

from subprocess import list2cmdline
from honcho.manager import Manager

from .base import cli


@cli.command()
@click.option("--scheduler/--no-scheduler", default=True)
@click.option("--processes", "-p", default=-1)
@click.option("--debug/--no-debug", default=False)
def worker(scheduler, processes, debug):
    os.environ["FLASK_DEBUG"] = "1" if debug else ""

    if processes == -1:
        processes = multiprocessing.cpu_count()

    daemons = []
    for n in range(processes):
        daemons.append(
            (
                "worker-{}".format(n),
                ["zeus", "service", "worker", "--debug" if debug else "--no-debug"],
            )
        )
    if scheduler:
        daemons.append(
            (
                "scheduler",
                ["zeus", "service", "scheduler", "--debug" if debug else "--no-debug"],
            )
        )

    cwd = os.path.realpath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )

    manager = Manager()
    for name, cmd in daemons:
        manager.add_process(
            name,
            list2cmdline(cmd),
            quiet=False,
            cwd=cwd,
            # env=os.environ,
        )

    manager.loop()
    sys.exit(manager.returncode)
