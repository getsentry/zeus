import os
import os.path
import re

from collections import namedtuple
from subprocess import Popen, PIPE
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Tuple
from uuid import UUID

from zeus.config import db
from zeus.db.utils import create_or_update, get_or_create
from zeus.models import Author, Repository, Revision

RevisionSaveResult = namedtuple("RevisionSaveResult", ["revision", "created"])

_author_re = re.compile(r"^(.+) <([^>]+)>$")

_co_authored_by_re = re.compile(
    r"^co-authored-by: (.+ <[^>]+>)$", re.MULTILINE | re.IGNORECASE
)


class RevisionResult(object):
    parents = None
    branches = None
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
        branches: Optional[List[str]] = None,
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
        if branches is not None:
            self.branches = branches
        if repository_id is not None:
            self.repository_id = repository_id
        self._author_cache = _author_cache or {}

    def __repr__(self) -> str:
        return "<%s: sha=%r author=%r subject=%r>" % (
            type(self).__name__,
            self.sha,
            self.author,
            self.subject,
        )

    def _parse_author_value(self, value: str) -> Tuple[str, str]:
        match = _author_re.match(value)
        if not match:
            if "@" in value:
                return value, value
            return value, "{0}@localhost".format(value)
        return match.group(1), match.group(2)

    def _get_author_instance(self, repository: Repository, email: str, name: str):
        key = (email, repository.id)
        result = self._author_cache.get(key)
        if result is not None:
            return result
        result = get_or_create(
            Author,
            where={"email": email, "repository_id": repository.id},
            defaults={"name": name},
        )[0]
        self._author_cache[key] = result
        return result

    def _get_authors(self, repository: Repository) -> List[Author]:
        name, email = self._parse_author_value(self.author)

        authors = [self._get_author_instance(repository, email, name)]

        for value in _co_authored_by_re.findall(self.message):
            name, email = self._parse_author_value(value)
            authors.append(self._get_author_instance(repository, email, name))

        return authors

    def _get_committer(self, repository: Repository) -> Author:
        name, email = self._parse_author_value(self.committer)
        return self._get_author_instance(repository, email, name)

    @property
    def date_created(self) -> str:
        return self.author_date

    @property
    def date_committed(self) -> Optional[str]:
        return self.committer_date

    @property
    def subject(self) -> str:
        return self.message.splitlines()[0]

    def save(self, repository: Repository) -> Tuple[Revision, bool]:
        authors = self._get_authors(repository)
        if self.author == self.committer:
            committer = authors[0]
        else:
            committer = self._get_committer(repository)

        with db.session.begin_nested():
            revision, created = create_or_update(
                Revision,
                where={"repository_id": repository.id, "sha": self.sha},
                values={
                    "author_id": authors[0].id,
                    "committer_id": committer.id,
                    "message": self.message,
                    "parents": self.parents,
                    "branches": self.branches,
                    "date_created": self.author_date,
                    "date_committed": self.committer_date,
                },
            )

            for author in authors:
                try:
                    with db.session.begin_nested():
                        revision.authors.append(author)
                except IntegrityError as exc:
                    if "duplicate" in str(exc):
                        continue
                    raise

        return RevisionSaveResult(revision, created)


class CommandError(Exception):
    def __init__(
        self,
        cmd: str = None,
        retcode: int = None,
        stdout: bytes = None,
        stderr: bytes = None,
    ):
        self.cmd = cmd
        self.retcode = retcode
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        if self.cmd:
            return "%s returned %d:\nSTDOUT: %r\nSTDERR: %r" % (
                self.cmd,
                self.retcode,
                self.stdout.decode("utf-8"),
                self.stderr.decode("utf-8"),
            )
        return ""


class UnknownRevision(CommandError):
    pass


class InvalidPublicKey(CommandError):
    pass


class BufferParser(object):
    def __init__(self, fp, delim):
        self.fp = fp
        self.delim = delim

    def __iter__(self):
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
            os.path.dirname(__file__), os.pardir, os.pardir, "bin", "ssh-connect"
        )
    )

    def __init__(self, id: str, path: str, url: str, username: Optional[str] = None):
        self.id = id
        self.path = path
        self.url = url
        self.username = username

        self._path_exists = None
        self._updated = False

    def get_default_env(self) -> dict:
        return {}

    def run(self, cmd, timeout=None, **kwargs) -> str:
        if self.exists():
            kwargs.setdefault("cwd", self.path)

        env = os.environ.copy()

        for key, value in self.get_default_env().items():
            env.setdefault(key, value)

        env.setdefault("ZEUS_SSH_REPO", self.id)

        for key, value in kwargs.pop("env", {}):
            env[key] = value

        kwargs["env"] = env
        kwargs["stdout"] = PIPE
        kwargs["stderr"] = PIPE

        proc = Popen(cmd, **kwargs)
        (stdout, stderr) = proc.communicate(timeout=timeout)
        if proc.returncode != 0:
            raise CommandError(cmd[0], proc.returncode, stdout, stderr)

        return stdout.decode("utf-8")

    def exists(self) -> bool:
        return os.path.exists(self.path)

    def clone(self):
        raise NotImplementedError

    def update(self, allow_cleanup=False):
        raise NotImplementedError

    def ensure(self, update_if_exists=True):
        if self._updated:
            return

        if not self.exists():
            self.clone()
        elif update_if_exists:
            self.update()
        self._updated = True

    def log(
        self,
        parent: str = None,
        branch: str = None,
        author: str = None,
        authors: List[str] = None,
        offset=0,
        limit=100,
    ) -> List[RevisionResult]:
        """ Gets the commit log for the repository.

        Only one of parent or branch can be specified for restricting searches.
        If parent is set, it is used to identify any ancestor revisions,
            regardless of their branch.
        If branch is set, all revisions in the branch AND any ancestor commits
            are returned.

        For any revisions returned, the list of associated branches returned is
        tool specific and may or may not include ancestor branch names. See tool
        implementations for exact behavior of this function.

        :param parent: Parent at which revision search begins.
        :param branch: Branch name the revision must be associated with.
        :param author: The author name or email to filter results.
        :param offset: An offset into the results at which to begin.
        :param limit: The maximum number of results to return.
        :return: A list of revisions matching the given criteria.
        """
        raise NotImplementedError

    def export(self, sha: str) -> str:
        """
        Show the changes (as a diff) in ``sha``.
        """
        raise NotImplementedError

    def show(self, sha: str, filename: str) -> str:
        """
        Show the contents of the ``filename`` at ``sha``.
        """
        raise NotImplementedError

    def get_default_branch(self) -> str:
        return self.get_default_revision()

    def get_default_revision(self) -> str:
        raise NotImplementedError

    def is_child_parent(self, child_in_question: str, parent_in_question: str) -> bool:
        raise NotImplementedError

    def get_known_branches(self) -> List[str]:
        """ This is limited to parallel trees with names.
        :return: A list of unique names for the branches.
        """
        raise NotImplementedError
