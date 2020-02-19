import click

from zeus import auth
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
from zeus.utils.asyncio import coroutine, create_db_pool
from zeus.utils.text import slugify
from zeus.vcs.client import vcs_client
from zeus.vcs.utils import get_vcs

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


@repos.command()
@click.argument("repository", required=True)
@click.argument("parent", default="master", required=False)
@click.option("--local", default=False, is_flag=True, required=False)
@click.option("--limit", default=100, required=False)
@coroutine
async def log(repository, parent, local, limit):
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

    if local:
        db_pool = await create_db_pool()

        async with db_pool.acquire() as conn:
            vcs = await get_vcs(conn, repo.id)

        results = vcs.log(parent=parent, limit=limit)

        for entry in results:
            click.echo(f"{entry.sha}\n  {entry.author}")
    else:
        tenant = auth.RepositoryTenant(repo.id)
        results = vcs_client.log(repo.id, parent=parent, limit=limit, tenant=tenant)

        for entry in results:
            click.echo(
                f"{entry['sha']}\n  {entry['authors'][0][0]} <{entry['authors'][0][1]}>"
            )
