import pytest

from subprocess import check_call

from zeus.vcs.asserts import assert_revision
from zeus.vcs.git import GitVcs


def _get_last_two_revisions(marker, revisions):
    if marker in revisions[0].branches:
        return revisions[0], revisions[1]

    else:
        return revisions[1], revisions[0]


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
def vcs(git_repo_config, default_repo):
    return GitVcs(
        url=git_repo_config.url, path=git_repo_config.path, id=default_repo.id.hex
    )


def test_get_default_revision(git_repo_config, vcs):
    assert vcs.get_default_revision() == "master"


def test_log_with_authors(git_repo_config, vcs):
    # Create a commit with a new author
    _set_author(git_repo_config.remote_path, "Another Committer", "ac@d.not.zm.exist")
    check_call(
        'cd %s && touch BAZ && git add BAZ && git commit -m "bazzy"'
        % git_repo_config.remote_path,
        shell=True,
    )
    vcs.clone()
    vcs.update()
    revisions = list(vcs.log())
    assert len(revisions) == 3

    revisions = list(vcs.log(author="Another Committer"))
    assert len(revisions) == 1
    assert_revision(
        revisions[0], author="Another Committer <ac@d.not.zm.exist>", message="bazzy"
    )

    revisions = list(vcs.log(author="ac@d.not.zm.exist"))
    assert len(revisions) == 1
    assert_revision(
        revisions[0], author="Another Committer <ac@d.not.zm.exist>", message="bazzy"
    )

    revisions = list(vcs.log(branch=vcs.get_default_revision(), author="Foo"))
    assert len(revisions) == 2


def test_log_throws_errors_when_needed(vcs):
    try:
        next(vcs.log(parent="HEAD", branch="master"))
        pytest.fail("log passed with both branch and master specified")
    except ValueError:
        pass


def test_log_with_branches(git_repo_config, vcs):
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
    vcs.clone()
    vcs.update()

    # Ensure git log normally includes commits from all branches
    revisions = list(vcs.log())
    assert len(revisions) == 4

    # Git timestamps are only accurate to the second. But since this test
    #   creates these commits so close to each other, there's a race
    #   condition here. Ultimately, we only care that both commits appear
    #   last in the log, so allow them to be out of order.
    last_rev, previous_rev = _get_last_two_revisions("B3", revisions)
    assert_revision(last_rev, message="3rd branch", branches=["B3"])
    assert_revision(previous_rev, message="second branch commit", branches=["B2"])

    # Note that the list of branches here differs from the hg version
    #   because hg only returns the branch name from the changeset, which
    #   does not include any ancestors.
    assert_revision(
        revisions[3], message="test", branches=[vcs.get_default_revision(), "B2", "B3"]
    )

    # Ensure git log with B3 only
    revisions = list(vcs.log(branch="B3"))
    assert len(revisions) == 3
    assert_revision(revisions[0], message="3rd branch", branches=["B3"])
    assert_revision(
        revisions[2], message="test", branches=[vcs.get_default_revision(), "B2", "B3"]
    )

    # Sanity check master
    check_call(
        "cd %s && git checkout %s" % (remote_path, vcs.get_default_revision()),
        shell=True,
    )
    revisions = list(vcs.log(branch=vcs.get_default_revision()))
    assert len(revisions) == 2


def test_simple(vcs):
    vcs.clone()
    vcs.update()
    revision = next(vcs.log(parent="HEAD", limit=1))
    assert len(revision.sha) == 40
    assert_revision(
        revision,
        author="Foo Bar <foo@example.com>",
        message="biz\nbaz\n",
        subject="biz",
    )
    revisions = list(vcs.log())
    assert len(revisions) == 2
    assert revisions[0].subject == "biz"
    assert revisions[0].message == "biz\nbaz\n"
    assert revisions[0].author == "Foo Bar <foo@example.com>"
    assert revisions[0].committer == "Foo Bar <foo@example.com>"
    assert revisions[0].parents == [revisions[1].sha]
    assert revisions[0].author_date == revisions[0].committer_date is not None
    assert revisions[0].branches == ["master"]
    assert revisions[1].subject == "test"
    assert revisions[1].message == "test\nlol\n"
    assert revisions[1].author == "Foo Bar <foo@example.com>"
    assert revisions[1].committer == "Foo Bar <foo@example.com>"
    assert revisions[1].parents == []
    assert revisions[1].author_date == revisions[1].committer_date is not None
    assert revisions[1].branches == ["master"]
    diff = vcs.export(revisions[0].sha)
    assert (
        diff
        == """diff --git a/BAR b/BAR
new file mode 100644
index 0000000..e69de29
"""
    )
    revisions = list(vcs.log(offset=0, limit=1))
    assert len(revisions) == 1
    assert revisions[0].subject == "biz"

    revisions = list(vcs.log(offset=1, limit=1))
    assert len(revisions) == 1
    assert revisions[0].subject == "test"


def test_is_child_parent(vcs):
    vcs.clone()
    vcs.update()
    revisions = list(vcs.log())
    assert vcs.is_child_parent(
        child_in_question=revisions[0].sha, parent_in_question=revisions[1].sha
    )
    assert (
        vcs.is_child_parent(
            child_in_question=revisions[1].sha, parent_in_question=revisions[0].sha
        )
        is False
    )


def test_get_known_branches(git_repo_config, vcs):
    vcs.clone()
    vcs.update()

    branches = vcs.get_known_branches()
    assert len(branches) == 1
    assert "master" in branches

    check_call(
        "cd %s && git checkout -B test_branch" % git_repo_config.remote_path, shell=True
    )
    vcs.update()
    branches = vcs.get_known_branches()
    assert len(branches) == 2
    assert "test_branch" in branches


def test_show(git_repo_config, vcs):
    check_call(
        'cd %s && echo "bar" > BAZ && git add BAZ && git commit -m "bazzy"'
        % git_repo_config.remote_path,
        shell=True,
    )

    vcs.clone()
    vcs.update()
    revisions = list(vcs.log())

    result = vcs.show(revisions[0].sha, "BAZ")
    assert result == "bar\n"
