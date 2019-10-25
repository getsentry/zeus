import click
import os
import socket
import sys

from subprocess import list2cmdline
from honcho.manager import Manager

from .base import cli

DEFAULT_HOST_NAME = socket.gethostname().split(".", 1)[0].lower()


@cli.command()
@click.option("--environment", default="development", help="The environment name.")
@click.option("--workers/--no-workers", default=False)
@click.option("--port", "-p", default=8080)
@click.option("--ngrok/--no-ngrok", default=False)
@click.option("--ngrok-domain", default="zeus-{}".format(DEFAULT_HOST_NAME))
@click.option("--pubsub/--no-pubsub", default=True)
@click.option("--pubsub-port", default=8090)
@click.option("--debug/--no-debug", default=True)
def devserver(
    environment, workers, port, ngrok, ngrok_domain, pubsub, pubsub_port, debug
):
    os.environ["FLASK_DEBUG"] = "1" if debug else ""
    os.environ["NODE_ENV"] = environment
    if pubsub:
        os.environ["PUBSUB_ENDPOINT"] = "http://localhost:{}".format(pubsub_port)

    if ngrok:
        root_url = "https://{}.ngrok.io".format(ngrok_domain)
        os.environ["SSL"] = "1"
        os.environ["SERVER_NAME"] = "{}.ngrok.io".format(ngrok_domain)
    else:
        root_url = "http://localhost:{}".format(port)

    click.echo("Launching Zeus on {}".format(root_url))

    # TODO(dcramer): pass required attributes to 'run' directly instead
    # of relying on FLASK_DEBUG
    daemons = [
        ("web", ["zeus", "run", "--port={}".format(port)]),
        (
            "webpack",
            [
                "node_modules/.bin/webpack",
                "--watch",
                "--config=config/webpack.config.js",
            ],
        ),
    ]
    if pubsub:
        daemons.append(("pubsub", ["zeus", "pubsub", "--port={}".format(pubsub_port)]))

    if workers:
        daemons.append(
            ("worker", ["zeus", "worker", "--scheduler", "--log-level=INFO"])
        )
    if ngrok:
        daemons.append(
            (
                "ngrok",
                ["ngrok", "http", "-subdomain={}".format(ngrok_domain), str(port)],
            )
        )

    cwd = os.path.realpath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )

    manager = Manager()
    for name, cmd in daemons:
        manager.add_process(name, list2cmdline(cmd), quiet=False, cwd=cwd)

    manager.loop()
    sys.exit(manager.returncode)
