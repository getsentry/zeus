import asyncio
import click
import os

from flask import current_app

from zeus.vcs.server import build_server

from .base import cli


@cli.command()
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8070, type=int)
def vcs_server(host, port):
    os.environ["PYTHONUNBUFFERED"] = "true"

    import logging

    current_app.logger.setLevel(logging.DEBUG)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(build_server(loop, host, port))
    print("vcs-server running on http://{}:{}".format(host, port))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Shutting Down!")
        loop.close()
