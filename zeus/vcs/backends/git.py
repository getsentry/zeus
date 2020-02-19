from typing import Iterator
from urllib.parse import urlparse

from zeus.exceptions import CommandError, InvalidPublicKey, UnknownRevision
from zeus.utils.functional import memoize
from zeus.utils import timezone

from .base import Vcs, RevisionResult, BufferParser

LOG_FORMAT = "%H\x01%an <%ae>\x01%at\x01%cn <%ce>\x01%ct\x01%P\x01%B\x02"

ORIGIN_PREFIX = "remotes/origin/"


class LazyGitRevisionResult(RevisionResult):
    def __init__(self, vcs: Vcs, *args, **kwargs):
        self.vcs = vcs
        super(LazyGitRevisionResult, self).__init__(*args, **kwargs)

    @memoize
    def branches(self):
        return self.vcs.branches_for_commit(self.sha)


class GitVcs(Vcs):
    binary_path = "git"

    def get_default_env(self) -> dict:
        return {"GIT_SSH": self.ssh_connect_path}

    def get_default_branch(self) -> str:
        return "master"

    def get_default_revision(self) -> str:
        return "master"

    @property
    def remote_url(self) -> str:
        if self.url.startswith("ssh:") and not self.username:
            username = "git"
        else:
            username = self.username
        if username and self.url.startswith(("ssh:", "http:", "https:")):
            parsed = urlparse(self.url)
            url = "%s://%s@%s/%s" % (
                parsed.scheme,
                parsed.username or username,
                parsed.hostname + (":%s" % (parsed.port,) if parsed.port else ""),
                parsed.path.lstrip("/"),
            )
        else:
            url = self.url
        return url

    def branches_for_commit(self, _id) -> list:
        return self.get_known_branches(commit_id=_id)

    def get_known_branches(self, commit_id=None) -> list:
        """ List all branches or those related to the commit for this repo.

        Either gets all the branches (if the commit_id is not specified) or then
        the branches related to the given commit reference.

        :param commit_id: A commit ID for fetching all related branches. If not
            specified, returns all branch names for this repository.
        :return: List of branches for the commit, or all branches for the repo.
        """
        results = []
        command_parameters = ["branch", "-a"]
        if commit_id:
            command_parameters.extend(["--contains", commit_id])
        output = self.run(command_parameters)

        for result in output.splitlines():
            # HACK(dcramer): is there a better way around removing the prefix?
            result = result[2:].strip()
            if result.startswith(ORIGIN_PREFIX):
                result = result[len(ORIGIN_PREFIX) :]
            if result == "HEAD":
                continue

            results.append(result)
        return list(set(results))

    def run(self, cmd, **kwargs) -> str:
        cmd = [self.binary_path] + cmd
        try:
            return super(GitVcs, self).run(cmd, **kwargs)

        except CommandError as e:
            stderr = e.stderr.decode("utf-8")
            if "unknown revision or path" in stderr:
                # fatal: ambiguous argument '82f750e7a3b692e049b95ed66bf9149f56218733^..82f750e7a3b692e049b95ed66bf9149f56218733': unknown revision or path not in the working tree.\nUse '--' to separate paths from revisions, like this:\n'git <command> [<revision>...] -- [<file>...]'\n
                raise UnknownRevision(
                    ref=stderr.split("fatal: ambiguous argument ")[-1].split("^", 1)[0],
                    cmd=e.cmd,
                    retcode=e.retcode,
                    stdout=e.stdout,
                    stderr=e.stderr,
                ) from e
            elif "fatal: bad object" in stderr:
                # bad object 5d953e751835a52472ca2e1906023435a71cb5e4\n
                raise UnknownRevision(
                    ref=stderr.split("\n")[0].split("bad object ", 1)[-1],
                    cmd=e.cmd,
                    retcode=e.retcode,
                    stdout=e.stdout,
                    stderr=e.stderr,
                ) from e

            if "Permission denied (publickey)" in stderr:
                raise InvalidPublicKey(
                    cmd=e.cmd, retcode=e.retcode, stdout=e.stdout, stderr=e.stderr
                ) from e

            raise

    def clone(self):
        self.run(["clone", "--mirror", self.remote_url, self.path])

    def update(self, allow_cleanup=False):
        if allow_cleanup:
            self.run(["fetch", "--all", "--force", "-p"])
        else:
            self.run(["fetch", "--all", "--force"])

    def log(
        self,
        parent=None,
        branch=None,
        author=None,
        offset=0,
        limit=100,
        timeout=None,
        update_if_exists=False,
    ) -> Iterator[LazyGitRevisionResult]:
        """ Gets the commit log for the repository.

        Each revision returned includes all the branches with which this commit
        is associated. There will always be at least one associated branch.

        See documentation for the base for general information on this function.
        """
        # TODO(dcramer): we should make this streaming
        cmd = ["log", "--date-order", "--pretty=format:%s" % (LOG_FORMAT,)]

        if author:
            cmd.append("--author=%s" % (author,))
        if offset:
            cmd.append("--skip=%d" % (offset,))
        if limit:
            cmd.append("--max-count=%d" % (limit,))

        if parent and branch:
            raise ValueError("Both parent and branch cannot be set")

        if branch:
            if branch == "!default":
                branch = self.get_default_branch()
            cmd.append(branch)

        # TODO(dcramer): determine correct way to paginate results in git as
        # combining --all with --parent causes issues
        elif not parent:
            cmd.append("--all")
        if parent:
            cmd.append(parent)

        for n in range(2):
            try:
                self.ensure(update_if_exists=update_if_exists)
                result = self.run(cmd, timeout=timeout)
                break
            except CommandError as cmd_error:
                err_msg = cmd_error.stderr
                if branch and branch in err_msg.decode("utf-8"):
                    # TODO: https://stackoverflow.com/questions/45096755/fatal-ambiguous-argument-origin-unknown-revision-or-path-not-in-the-working
                    default_error = ValueError(
                        'Unable to fetch commit log for branch "{0}".'.format(branch)
                    )
                    if not self.run(["remote"]):
                        # assume we're in a broken state, and try to repair
                        # XXX: theory is this might happen when OOMKiller axes clone?
                        result = self.run(
                            [
                                "symbolic-ref",
                                "refs/remotes/origin/HEAD",
                                "refs/remotes/origin/{}".format(
                                    self.get_default_branch()
                                ),
                            ]
                        )
                        continue

                    import traceback
                    import logging

                    msg = traceback.format_exception(CommandError, cmd_error, None)
                    logging.warning(msg)
                    raise default_error from cmd_error
                raise

        for chunk in BufferParser(result, "\x02"):
            (
                sha,
                author,
                author_date,
                committer,
                committer_date,
                parents,
                message,
            ) = chunk.split("\x01")

            # sha may have a trailing newline due to git log adding it
            sha = sha.lstrip("\n")

            parents = [p for p in parents.split(" ") if p]

            author_date = timezone.fromtimestamp(float(author_date))
            committer_date = timezone.fromtimestamp(float(committer_date))

            yield LazyGitRevisionResult(
                vcs=self,
                sha=sha,
                author=author,
                committer=committer,
                author_date=author_date,
                committer_date=committer_date,
                parents=parents,
                message=message,
            )

    def export(self, sha, update_if_exists=False) -> str:
        cmd = ["diff", "%s^..%s" % (sha, sha)]
        self.ensure(update_if_exists=update_if_exists)
        result = self.run(cmd)
        return result

    def show(self, sha, filename, update_if_exists=False) -> str:
        cmd = ["show", "{}:{}".format(sha, filename)]
        self.ensure(update_if_exists=update_if_exists)
        result = self.run(cmd)
        return result

    def is_child_parent(self, child_in_question, parent_in_question) -> bool:
        cmd = ["merge-base", "--is-ancestor", parent_in_question, child_in_question]
        self.ensure()
        try:
            self.run(cmd)
            return True

        except CommandError:
            return False
