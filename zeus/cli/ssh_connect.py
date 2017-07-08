import click
import os
import subprocess
import sys

from tempfile import NamedTemporaryFile

from zeus.config import db
from zeus.models import ItemOption, Repository

from .base import cli


@cli.command('ssh-connect')
@click.argument('repository-url', envvar='SSH_REPO', required=True)
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def ssh_connect(repository_url, args):
    repo = Repository.query.filter_by(url=repository_url).first()
    if not repo:
        click.echo('Unable to find repository', err=True)
        sys.exit(1)

    options = dict(
        db.session.query(ItemOption.name, ItemOption.value).filter(
            ItemOption.item_id == repo.id,
            ItemOption.name.in_([
                'auth.private-key',
                'auth.private-key-file',
            ])
        )
    )

    command = [
        'ssh',
        # Not supported in all ssh client versions
        # '-o UserAuthorizedKeysFile=/dev/null',
        '-o LogLevel=ERROR',
        '-o StrictHostKeyChecking=no',
        '-o UserKnownHostsFile=/dev/null',
    ]
    if options.get('auth.private-key'):
        f = NamedTemporaryFile()
        f.write(options['auth.private-key'])
        f.close()
        command.append('-i {0}'.format(f.name))
    elif options.get('auth.private-key-file'):
        command.append('-i {0}'.format(options['auth.private-key-file']))

    command.append('--')

    command.extend(args)

    sys.exit(
        subprocess.call(
            command,
            cwd=os.getcwd(),
            env=os.environ,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    )
