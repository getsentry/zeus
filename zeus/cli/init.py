import binascii
import click
import os
import sys

from subprocess import list2cmdline
from honcho.manager import Manager

from .base import cli


CONFIG = """
SECRET_KEY = {secret_key}

GITHUB_CLIENT_ID = None
GITHUB_CLIENT_SECRET = None
""".strip()


@cli.command(help='Create default configuration.')
@click.argument('path', default='~/.zeus/')
def init(path):
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        os.makedirs(path)

    with open(os.path.join(path, 'zeus.config.py'), 'wb') as fp:
        fp.write(CONFIG.format(
            secret_key=repr(binascii.hexlify(os.urandom(24))),
        ).encode('utf-8'))
