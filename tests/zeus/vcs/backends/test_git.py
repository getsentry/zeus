import pytest

from subprocess import check_call
from uuid import UUID

from zeus.vcs.asserts import assert_revision
from zeus.vcs.backends.git import GitVcs


def _set_author(remote_path, name, email):
    check_call(
        'cd {0} && git config --replace-all "user.name" "{1}"'.format(
            remote_path, name
        ),
        shell=True,
    )
    check_call(
        'cd {0} && git config --replace-all "user.email" "{1}"'.format(
            remote_path, email
        ),
        shell=True,
    )


@pytest.fixture
async def vcs(git_repo_config, default_repo_id: UUID):
    return GitVcs(
        url=git_repo_config.url, path=git_repo_config.path, id=default_repo_id.hex
    )


def test_get_default_revision(git_repo_config, vcs):
    assert vcs.get_default_revision() == "master"


async def test_log_with_authors(git_repo_config, vcs):
    # Create a commit with a new author
    _set_author(git_repo_config.remote_path, "Another Committer", "ac@d.not.zm.exist")
    check_call(
        'cd %s && touch BAZ && git add BAZ && git commit -m "bazzy"'
        % git_repo_config.remote_path,
        shell=True,
    )
    await vcs.clone()
    await vcs.update()
    revisions = await vcs.log()
    assert len(revisions) == 3

    revisions = await vcs.log(author="Another Committer")
    assert len(revisions) == 1
    assert_revision(
        revisions[0], author="Another Committer <ac@d.not.zm.exist>", message="bazzy"
    )

    revisions = await vcs.log(author="ac@d.not.zm.exist")
    assert len(revisions) == 1
    assert_revision(
        revisions[0], author="Another Committer <ac@d.not.zm.exist>", message="bazzy"
    )

    revisions = await vcs.log(branch=vcs.get_default_revision(), author="Foo")
    assert len(revisions) == 2


async def test_log_throws_errors_when_needed(vcs):
    try:
        await vcs.log(parent="HEAD", branch="master")
        pytest.fail("log passed with both branch and master specified")
    except ValueError:
        pass


async def test_log_with_branches(git_repo_config, vcs):
    # Create another branch and move it ahead of the master branch
    remote_path = git_repo_config.remote_path
    check_call("cd %s && git checkout -b B2" % remote_path, shell=True)
    check_call(
        'cd %s && touch BAZ && git add BAZ && git commit -m "second branch commit"'
        % (remote_path,),
        shell=True,
    )

    # Create a third branch off master with a commit not in B2
    check_call(
        "cd %s && git checkout %s" % (remote_path, vcs.get_default_revision()),
        shell=True,
    )
    check_call("cd %s && git checkout -b B3" % remote_path, shell=True)
    check_call(
        'cd %s && touch IPSUM && git add IPSUM && git commit -m "3rd branch"'
        % (remote_path,),
        shell=True,
    )
    await vcs.clone()
    await vcs.update()

    # Ensure git log with B3 only
    revisions = await vcs.log(branch="B3")
    assert len(revisions) == 3
    assert_revision(revisions[0], message="3rd branch")
    assert_revision(revisions[2], message="test")

    # Sanity check master
    check_call(
        "cd %s && git checkout %s" % (remote_path, vcs.get_default_revision()),
        shell=True,
    )
    revisions = await vcs.log(branch=vcs.get_default_revision())
    assert len(revisions) == 2


async def test_simple(vcs):
    await vcs.clone()
    await vcs.update()
    revision = (await vcs.log(parent="HEAD", limit=1))[0]
    assert len(revision.sha) == 40
    assert_revision(revision, author="Foo Bar <foo@example.com>", message="biz\nbaz\n")
    revisions = await vcs.log()
    assert len(revisions) == 2
    assert revisions[0].message == "biz\nbaz\n"
    assert revisions[0].author == "Foo Bar <foo@example.com>"
    assert revisions[0].committer == "Foo Bar <foo@example.com>"
    assert revisions[0].parents == [revisions[1].sha]
    assert revisions[0].author_date == revisions[0].committer_date is not None
    assert revisions[1].message == "test\nlol\n"
    assert revisions[1].author == "Foo Bar <foo@example.com>"
    assert revisions[1].committer == "Foo Bar <foo@example.com>"
    assert revisions[1].parents == []
    assert revisions[1].author_date == revisions[1].committer_date is not None
    diff = await vcs.export(revisions[0].sha)
    assert (
        diff
        == """diff --git a/BAR b/BAR
new file mode 100644
index 0000000..e69de29
"""
    )
    revisions = await vcs.log(offset=0, limit=1)
    assert len(revisions) == 1
    assert revisions[0].message == "biz\nbaz\n"

    revisions = await vcs.log(offset=1, limit=1)
    assert len(revisions) == 1
    assert revisions[0].message == "test\nlol\n"


async def test_get_known_branches(git_repo_config, vcs):
    await vcs.clone()
    await vcs.update()

    branches = await vcs.get_known_branches()
    assert len(branches) == 1
    assert "master" in branches

    check_call(
        "cd %s && git checkout -B test_branch" % git_repo_config.remote_path, shell=True
    )
    await vcs.update()
    branches = await vcs.get_known_branches()
    assert len(branches) == 2
    assert "test_branch" in branches


async def test_show(git_repo_config, vcs):
    check_call(
        'cd %s && echo "bar" > BAZ && git add BAZ && git commit -m "bazzy"'
        % git_repo_config.remote_path,
        shell=True,
    )

    await vcs.clone()
    await vcs.update()
    revisions = await vcs.log()

    result = await vcs.show(revisions[0].sha, "BAZ")
    assert result == "bar\n"
