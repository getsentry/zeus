import click
import os

from .base import cli


@cli.command()
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8080, type=int)
@click.option("--processes", default=1, type=int)
@click.option("--threads", default=4, type=int)
def web(host, port, processes, threads):
    os.environ["PYTHONUNBUFFERED"] = "true"

    import mywsgi

    mywsgi.run(
        "zeus.app:app",
        "{}:{}".format(host, port),
        processes=processes,
        threads=threads,
        buffer_size=32768,
        post_buffering=65536,
        harakiri=120,
        harakiri_verbose=True,
        # XXX(dcramer): this is disabled as our version of uwsgi doesnt
        # know what it means
        # wsgi_manage_chunked_input=True,
    )
