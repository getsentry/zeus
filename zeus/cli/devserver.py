import click
import os
import sys

from subprocess import list2cmdline
from honcho.manager import Manager

from .base import cli


@cli.command()
@click.option('--environment', default='development', help='The environment name.')
def devserver(environment):
    os.environ.setdefault('FLASK_DEBUG', '1')
    os.environ['NODE_ENV'] = environment

    # TODO(dcramer): pass required attributes to 'run' directly instead
    # of relying on FLASK_DEBUG
    daemons = [
        ('web', ['zeus', 'run']),
        ('webpack', ['node_modules/.bin/webpack', '--watch',
                     '--config=config/webpack.config.dev.js']),
    ]

    cwd = os.path.realpath(os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir))

    manager = Manager()
    for name, cmd in daemons:
        manager.add_process(
            name, list2cmdline(cmd),
            quiet=False, cwd=cwd,
        )

    manager.loop()
    sys.exit(manager.returncode)
