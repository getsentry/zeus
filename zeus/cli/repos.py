import click

from zeus.config import db
from zeus.models import Repository, RepositoryAccess, RepositoryBackend, RepositoryStatus, User
from zeus.tasks import import_repo, sync_repo
from zeus.utils.text import slugify

from .base import cli


@cli.group('repos')
def repos():
    pass


@repos.command()
@click.argument('repository_full_name', required=True)
@click.option('--backend', default='git', type=click.Choice(['git']))
@click.option('--url')
@click.option('--active/--inactive', default=True)
def add(repository_full_name, url, backend, active):
    raise NotImplementedError
    owner_name, repo_name = repository_full_name.split('/', 1)
    repo = Repository(
        url=url,
        owner_name=slugify(owner_name),
        name=slugify(repo_name),
        backend=getattr(RepositoryBackend, backend),
        status=RepositoryStatus.active if active else RepositoryStatus.inactive,
    )
    db.session.add(repo)
    db.session.commit()

    if active:
        # do initial import in process
        import_repo(repo_id=repo.id)


@repos.command()
@click.argument('repository_full_name', required=True)
def sync(repository_full_name):
    owner_name, repo_name = repository_full_name.split('/', 1)
    repo = Repository.query.unrestricted_unsafe().filter(
        Repository.owner_name == owner_name,
        Repository.name == repo_name,
    ).first()
    sync_repo(repo_id=repo.id)


@repos.group('access')
def access():
    pass


@access.command('add')
@click.argument('repository_full_name', required=True)
@click.argument('email', required=True)
def access_add(repository_full_name, email):
    owner_name, repo_name = repository_full_name.split('/', 1)
    repo = Repository.query.unrestricted_unsafe().filter(
        Repository.owner_name == owner_name,
        Repository.name == repo_name,
    ).first()
    user = User.query.filter(User.email == email).first()
    assert repo
    assert email
    access = RepositoryAccess(user=user, repository=repo)
    db.session.add(access)
    db.session.commit()
