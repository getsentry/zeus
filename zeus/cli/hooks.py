import click
import sys

from base64 import urlsafe_b64encode

from zeus.config import db
from zeus.models import Repository, Hook

from .base import cli


@cli.group('hooks')
def hooks():
    pass


@hooks.command()
@click.argument('repository_url', required=True)
@click.argument('provider', required=True)
def add(repository_url, provider):
    repo = Repository.query.unrestricted_unsafe().filter(
        Repository.url == repository_url,
    ).first()
    assert repo

    hook = Hook(
        repository_id=repo.id,
        provider=provider,
    )
    db.session.add(hook)
    db.session.commit()

    click.echo('Hook created:')
    click.echo('-> id           = {}'.format(str(hook.id)))
    click.echo('-> token        = {}'.format(urlsafe_b64encode(hook.token).decode('utf-8')))
    click.echo('-> provider     = {}'.format(hook.provider))
    click.echo('-> base_path    = /hooks/{}/{}'.format(str(hook.id), hook.get_signature()))


@hooks.command()
@click.option('--provider')
def list(provider):
    query = Hook.query.unrestricted_unsafe()
    if provider:
        query = query.filter(Hook.provider == provider)

    click.echo('Registered Hooks:')
    for hook in query:
        click.echo(' -> {} ({})'.format(hook.id, hook.provider))


@hooks.command()
@click.argument('hook_id', required=True)
@click.option(
    '--yes', prompt='Are you sure you wish to remove this hook?', is_flag=True, required=True
)
def remove(hook_id, yes):
    if not yes:
        sys.exit(1)
    hook = Hook.query.unrestricted_unsafe().get(hook_id)
    assert hook
    db.session.delete(hook)
    db.session.commit()

    click.echo('Hook deleted!')
