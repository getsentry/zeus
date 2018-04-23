import binascii
import click
import os

from .base import cli

CONFIG = """
import os.path

SECRET_KEY = {secret_key}

GITHUB_CLIENT_ID = {github_client_id}
GITHUB_CLIENT_SECRET = {github_client_secret}

WORKSPACE_ROOT = {workspace_root}
REPO_ROOT = os.path.join(WORKSPACE_ROOT, 'repo-cache')
""".strip()


@cli.command(help="Create default configuration.")
@click.option("--github-client-id", prompt="GitHub Client ID", help="GitHub Client ID")
@click.option(
    "--github-client-secret", prompt="GitHub Client Secret", help="GitHub Client Secret"
)
@click.argument("path", default="~/.zeus/")
def init(path, github_client_id, github_client_secret):
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        os.makedirs(path)

    config_path = os.path.join(path, "zeus.config.py")
    if os.path.exists(config_path):
        click.confirm(
            "Configuration file already present at [{}]. Overwrite it?".format(
                config_path
            ),
            abort=True,
        )

    with open(config_path, "wb") as fp:
        fp.write(
            CONFIG.format(
                secret_key=repr(binascii.hexlify(os.urandom(24))),
                github_client_id=repr(github_client_id),
                github_client_secret=repr(github_client_secret),
                workspace_root=repr(path),
            ).encode(
                "utf-8"
            )
        )
    click.echo("Configuration written at {}".format(config_path))
