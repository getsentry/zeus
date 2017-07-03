import binascii
import click
import os
import sys

from .base import cli


CONFIG = """
SECRET_KEY = {secret_key}

GITHUB_CLIENT_ID = {github_client_id}
GITHUB_CLIENT_SECRET = {github_client_secret}
""".strip()


@cli.command(help='Create default configuration.')
@click.option('--no-input', default=False, help='Dont prompt for input.')
@click.option('--github-client-id', help='GitHub Client ID')
@click.option('--github-client-secret', help='GitHub Client Secret')
@click.argument('path', default='~/.zeus/')
def init(path, no_input, github_client_id, github_client_secret):
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        os.makedirs(path)

    config_path = os.path.join(path, 'zeus.config.py')
    if os.path.exists(config_path):
        print('Configuration file already present at {}'.format(config_path))
        if input('Overwrite it? [yN] ').lower() != 'y':
            sys.exit(0)

    if not no_input:
        if not github_client_id:
            github_client_id = input('GitHub Client ID? ')
        if not github_client_secret:
            github_client_secret = input('GitHub Client Secret? ')

    with open(config_path, 'wb') as fp:
        fp.write(CONFIG.format(
            secret_key=repr(binascii.hexlify(os.urandom(24))),
            github_client_id=repr(github_client_id),
            github_client_secret=repr(github_client_secret),
        ).encode('utf-8'))
    print('Configuration written at {}'.format(config_path))
