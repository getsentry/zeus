import click
import os
import subprocess
import sys

from tempfile import NamedTemporaryFile

from zeus import auth
from zeus.config import db
from zeus.models import ItemOption, Repository, RepositoryProvider

from .base import cli


@cli.command("ssh-connect")
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.option("--repository", envvar="ZEUS_SSH_REPO", required=True)
def ssh_connect(args, repository):
    if "/" in repository:
        r_provider, r_owner, r_name = repository.split("/", 2)
        repo = (
            Repository.query.unrestricted_unsafe()
            .filter(
                Repository.provider == RepositoryProvider(r_provider),
                Repository.owner_name == r_owner,
                Repository.name == r_name,
            )
            .first()
        )
    else:
        repo = Repository.query.unrestricted_unsafe().get(repository)
    if not repo:
        click.echo("Unable to find repository", err=True)
        sys.exit(1)

    auth.set_current_tenant(auth.RepositoryTenant(repo.id))

    options = dict(
        db.session.query(ItemOption.name, ItemOption.value).filter(
            ItemOption.item_id == repo.id,
            ItemOption.name.in_(["auth.private-key", "auth.private-key-file"]),
        )
    )

    command = [
        "ssh",
        # Not supported in all ssh client versions
        # '-oUserAuthorizedKeysFile=/dev/null',
        "-oLogLevel=ERROR",
        "-oStrictHostKeyChecking=no",
        "-oUserKnownHostsFile=/dev/null",
    ]
    tmp_file = None
    if options.get("auth.private-key"):
        tmp_file = NamedTemporaryFile(delete=False)
        tmp_file.write(options["auth.private-key"].encode("utf-8"))
        tmp_file.close()
        command.append("-i{0}".format(tmp_file.name))
    elif options.get("auth.private-key-file"):
        command.append("-i{0}".format(options["auth.private-key-file"]))

    command.append("--")

    command.extend(args)

    try:
        exit_code = subprocess.call(
            command,
            cwd=os.getcwd(),
            env=os.environ,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    finally:
        if tmp_file:
            os.unlink(tmp_file.name)
    sys.exit(exit_code)
