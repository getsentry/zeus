import click
import os
import subprocess
import sys

from .base import cli


@cli.command()
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8080, type=int)
@click.option("--processes", default=1, type=int)
@click.option("--threads", default=4, type=int)
def web(host, port, processes, threads):
    os.environ["PYTHONUNBUFFERED"] = "true"

    cmd = [
        "uwsgi",
        "--master",
        "--vacuum",
        "--enable-threads",
        # "--lazy-apps",
        "--single-interpreter",
        "--http={}:{}".format(host, port),
        "--processes={}".format(processes),
        "--threads={}".format(threads),
        "--log-x-forwarded-for",
        "--buffer-size=32768",
        "--post-buffering=65536",
        "--need-app",
        "--harakiri=120",
        "--harakiri-verbose",
        "--thunder-lock",
        "--vacuum",
        "--home={}".format(sys.prefix),
        "--auto-procname",
        "--procname-prefix-spaced=[zeus]",
        "--module=zeus.app:app",
        "--die-on-term",
        "--ignore-sigpipe",
        "--ignore-write-errors",
        "--disable-write-exception",
        # XXX(dcramer): this is disabled as our version of uwsgi doesnt
        # know what it means
        # '--wsgi-manage-chunked-input',
    ]

    cwd = os.path.realpath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
    sys.exit(subprocess.call(cmd, cwd=cwd))
