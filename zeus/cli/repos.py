import click

from zeus.config import db
from zeus.db.utils import create_or_update
from zeus.models import (
    ItemOption,
    Repository,
    RepositoryAccess,
    RepositoryBackend,
    RepositoryProvider,
    RepositoryStatus,
    User,
)
from zeus.tasks import import_repo, sync_repo
from zeus.utils.text import slugify

from .base import cli


@cli.group("repos")
def repos():
    pass


@repos.command()
@click.argument("repository", required=True)
@click.option("--backend", default="git", type=click.Choice(["git"]))
@click.option("--url")
@click.option("--active/--inactive", default=True)
def add(repository, url, backend, active):
    raise NotImplementedError

    provider, owner_name, repo_name = repository.split("/", 2)
    repo = Repository(
        url=url,
        owner_name=slugify(owner_name),
        provider=RepositoryProvider(provider),
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
@click.argument("repository", required=True)
def sync(repository):
    provider, owner_name, repo_name = repository.split("/", 2)
    repo = (
        Repository.query.unrestricted_unsafe()
        .filter(
            Repository.provider == RepositoryProvider(provider),
            Repository.owner_name == owner_name,
            Repository.name == repo_name,
        )
        .first()
    )
    sync_repo(repo_id=repo.id, force=True)


@repos.group("access")
def access():
    pass


@access.command("add")
@click.argument("repository", required=True)
@click.argument("email", required=True)
def access_add(repository, email):
    provider, owner_name, repo_name = repository.split("/", 2)
    repo = (
        Repository.query.unrestricted_unsafe()
        .filter(
            Repository.provider == RepositoryProvider(provider),
            Repository.owner_name == owner_name,
            Repository.name == repo_name,
        )
        .first()
    )
    user = User.query.filter(User.email == email).first()
    assert repo
    assert email
    access = RepositoryAccess(user=user, repository=repo)
    db.session.add(access)
    db.session.commit()


@repos.group("config")
def config():
    pass


@config.command("get")
@click.argument("repository", required=True)
@click.argument("option", required=True, nargs=-1)
def config_get(repository, option):
    provider, owner_name, repo_name = repository.split("/", 2)
    repo = (
        Repository.query.unrestricted_unsafe()
        .filter(
            Repository.provider == RepositoryProvider(provider),
            Repository.owner_name == owner_name,
            Repository.name == repo_name,
        )
        .first()
    )

    for key in option:
        result = (
            db.session.query(ItemOption.value)
            .filter(ItemOption.item_id == repo.id, ItemOption.name == key)
            .first()
        )
        click.echo("{} = {}".format(key, result[0] if result else "(not set)"))


@config.command("set")
@click.argument("repository", required=True)
@click.argument("option", required=True, nargs=-1)
def config_set(repository, option):
    provider, owner_name, repo_name = repository.split("/", 2)
    repo = (
        Repository.query.unrestricted_unsafe()
        .filter(
            Repository.provider == RepositoryProvider(provider),
            Repository.owner_name == owner_name,
            Repository.name == repo_name,
        )
        .first()
    )

    for key, value in [o.split("=", 1) for o in option]:
        create_or_update(
            ItemOption, where={"item_id": repo.id, "name": key}, values={"value": value}
        )
    db.session.commit()
