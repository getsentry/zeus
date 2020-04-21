import asyncio
import os
import os.path
import re

from typing import Iterator, List, Optional, Tuple
from uuid import UUID

from zeus.exceptions import CommandError

_author_re = re.compile(r"^(.+) <([^>]+)>$")

_co_authored_by_re = re.compile(
    r"^co-authored-by: (.+ <[^>]+>)$", re.MULTILINE | re.IGNORECASE
)


class RevisionResult(object):
    parents = None
    repository_id = None

    def __init__(
        self,
        sha: str,
        message: str,
        author: str,
        author_date,
        committer: str = None,
        committer_date=None,
        parents: Optional[List[str]] = None,
        repository_id: UUID = None,
        _author_cache: dict = None,
    ):
        self.sha = sha
        self.message = message
        self.author = author
        self.author_date = author_date
        self.committer = committer or author
        self.committer_date = committer_date or author_date
        if parents is not None:
            self.parents = parents
        if repository_id is not None:
            self.repository_id = repository_id

    def __repr__(self) -> str:
        return "<%s: sha=%r author=%r subject=%r>" % (
            type(self).__name__,
            self.sha,
            self.author,
            self.message.splitlines()[0],
        )

    def _parse_author_value(self, value: str) -> Tuple[str, str]:
        match = _author_re.match(value)
        if not match:
            if "@" in value:
                return value, value
            return value, "{0}@localhost".format(value)
        return match.group(1), match.group(2)

    def get_authors(self) -> List[Tuple[str, str]]:
        name, email = self._parse_author_value(self.author)

        authors = [(name, email)]

        for value in _co_authored_by_re.findall(self.message):
            name, email = self._parse_author_value(value)
            authors.append((name, email))

        return authors

    def get_committer(self) -> Tuple[str, str]:
        return self._parse_author_value(self.committer or self.author)


class BufferParser(object):
    def __init__(self, fp, delim: str):
        self.fp = fp
        self.delim = delim

    def __iter__(self) -> Iterator[str]:
        chunk_buffer = []
        for chunk in self.fp:
            while chunk.find(self.delim) != -1:
                d_pos = chunk.find(self.delim)

                chunk_buffer.append(chunk[:d_pos])

                yield "".join(chunk_buffer)

                chunk_buffer = []

                chunk = chunk[d_pos + 1 :]

            if chunk:
                chunk_buffer.append(chunk)

        if chunk_buffer:
            yield "".join(chunk_buffer)


class Vcs(object):
    ssh_connect_path = os.path.realpath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            os.pardir,
            os.pardir,
            "bin",
            "ssh-connect",
        )
    )

    def __init__(self, id: str, path: str, url: str, username: Optional[str] = None):
        self.id = id
        self.path = path
        self.url = url
        self.username = username

        self._path_exists = None

    def get_default_env(self) -> dict:
        return {}

    async def run(self, cmd, timeout=None, **kwargs) -> str:
        if self.exists():
            kwargs.setdefault("cwd", self.path)

        env = os.environ.copy()

        for key, value in self.get_default_env().items():
            env.setdefault(key, value)

        env.setdefault("ZEUS_SSH_REPO", self.id)

        for key, value in kwargs.pop("env", {}):
            env[key] = value

        kwargs["env"] = env
        kwargs["stdout"] = asyncio.subprocess.PIPE
        kwargs["stderr"] = asyncio.subprocess.PIPE

        proc = await asyncio.create_subprocess_exec(*cmd, **kwargs)
        (stdout, stderr) = await asyncio.wait_for(proc.communicate(), timeout)
        if proc.returncode != 0:
            raise CommandError(cmd[0], proc.returncode, stdout, stderr)

        return stdout.decode()

    def exists(self) -> bool:
        return os.path.exists(self.path)

    async def cleanup(self):
        return

    async def clone(self):
        raise NotImplementedError

    async def update(self, allow_cleanup=False):
        raise NotImplementedError

    async def ensure(self, update_if_exists=True):
        if not self.exists():
            await self.clone()
        elif update_if_exists:
            await self.update()

    async def log(
        self,
        parent: str = None,
        branch: str = None,
        author: str = None,
        authors: List[str] = None,
        offset=0,
        limit=100,
        update_if_exists=False,
    ) -> Iterator[RevisionResult]:
        """ Gets the commit log for the repository.

        Only one of parent or branch can be specified for restricting searches.
        If parent is set, it is used to identify any ancestor revisions,
            regardless of their branch.
        If branch is set, all revisions in the branch AND any ancestor commits
            are returned.

        :param parent: Parent at which revision search begins.
        :param branch: Branch name the revision must be associated with.
        :param author: The author name or email to filter results.
        :param offset: An offset into the results at which to begin.
        :param limit: The maximum number of results to return.
        :return: An iterator of revisions matching the given criteria.
        """
        raise NotImplementedError

    async def export(self, sha: str) -> str:
        """
        Show the changes (as a diff) in ``sha``.
        """
        raise NotImplementedError

    async def show(self, sha: str, filename: str) -> str:
        """
        Show the contents of the ``filename`` at ``sha``.
        """
        raise NotImplementedError

    async def get_known_branches(self) -> List[str]:
        """ This is limited to parallel trees with names.
        :return: A list of unique names for the branches.
        """
        raise NotImplementedError

    def get_default_branch(self) -> str:
        return self.get_default_revision()

    def get_default_revision(self) -> str:
        raise NotImplementedError
