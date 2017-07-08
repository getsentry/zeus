import click

from zeus.config import db
from zeus.models import Repository, RepositoryBackend, RepositoryStatus
from zeus.tasks import import_repo, sync_repo

from .base import cli


@cli.group('repos')
def repos():
    pass


@repos.command()
@click.argument('repository_url', required=True)
@click.option('--backend', default='git', type=click.Choice(['git']))
@click.option('--active/--inactive', default=True)
def add(repository_url, backend, active):
    repo = Repository(
        url=repository_url,
        backend=getattr(RepositoryBackend, backend),
        status=RepositoryStatus.active if active else RepositoryStatus.inactive, )
    db.session.add(repo)

    if active:
        # do initial import in process
        import_repo(repo_id=repo.id)


@repos.command()
@click.argument('repository_url', required=True)
def sync(repository_url):
    repo = Repository.query.filter(
        Repository.url == repository_url, ).first()
    sync_repo(repo_id=repo.id)
