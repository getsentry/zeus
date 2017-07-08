import click
import os
import sys

from subprocess import list2cmdline
from honcho.manager import Manager

from .base import cli


@cli.command()
@click.option('--environment', default='development', help='The environment name.')
@click.option('--workers/--no-workers', default=False)
def devserver(environment, workers):
    os.environ.setdefault('FLASK_DEBUG', '1')
    os.environ['NODE_ENV'] = environment

    # TODO(dcramer): pass required attributes to 'run' directly instead
    # of relying on FLASK_DEBUG
    daemons = [
        ('web', ['zeus', 'run']),
        (
            'webpack',
            ['node_modules/.bin/webpack', '--watch', '--config=config/webpack.config.dev.js']
        ),
    ]
    if workers:
        daemons.append(('worker', ['zeus', 'worker', '--cron', '--log-level=INFO']))

    cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

    manager = Manager()
    for name, cmd in daemons:
        manager.add_process(
            name,
            list2cmdline(cmd),
            quiet=False,
            cwd=cwd,
        )

    manager.loop()
    sys.exit(manager.returncode)
