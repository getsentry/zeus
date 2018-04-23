import click
import os
import sys

from subprocess import list2cmdline
from honcho.manager import Manager

from .base import cli


@cli.command()
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8080, type=int)
@click.option("--processes", default=1, type=int)
@click.option("--threads", default=4, type=int)
def web(host, port, processes, threads):
    os.environ["PYTHONUNBUFFERED"] = "true"

    daemons = [
        (
            "web",
            [
                "uwsgi",
                "--master",
                "--enable-threads",
                "--lazy-apps",
                "--single-interpreter",
                "--http={}:{}".format(host, port),
                "--processes={}".format(processes),
                "--threads={}".format(threads),
                "--log-x-forwarded-for",
                "--buffer-size=32768",
                "--post-buffering=65536",
                "--need-app",
                # '--disable-logging',
                "--thunder-lock",
                "--vacuum",
                "--home={}".format(sys.prefix),
                "--auto-procname",
                "--procname-prefix-spaced=[zeus]",
                "--module=zeus.app:app",
                "--die-on-term",
                # XXX(dcramer): this is disabled as our version of uwsgi doesnt
                # know what it means
                # '--wsgi-manage-chunked-input',
            ],
        )
    ]

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
