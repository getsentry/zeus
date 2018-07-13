
            remote_path, name
        ),
        shell=True,
            remote_path, email
        ),
        shell=True,
    return GitVcs(
        url=git_repo_config.url, path=git_repo_config.path, id=default_repo.id.hex
    )
    assert vcs.get_default_revision() == "master"
    _set_author(git_repo_config.remote_path, "Another Committer", "ac@d.not.zm.exist")
        'cd %s && touch BAZ && git add BAZ && git commit -m "bazzy"'
        % git_repo_config.remote_path,
        shell=True,
    revisions = list(vcs.log(author="Another Committer"))
        revisions[0], author="Another Committer <ac@d.not.zm.exist>", message="bazzy"
    )
    revisions = list(vcs.log(author="ac@d.not.zm.exist"))
        revisions[0], author="Another Committer <ac@d.not.zm.exist>", message="bazzy"
    )
    revisions = list(vcs.log(branch=vcs.get_default_revision(), author="Foo"))
        next(vcs.log(parent="HEAD", branch="master"))
        pytest.fail("log passed with both branch and master specified")
    check_call("cd %s && git checkout -b B2" % remote_path, shell=True)
        'cd %s && touch BAZ && git add BAZ && git commit -m "second branch commit"'
        % (remote_path,),
        shell=True,
        "cd %s && git checkout %s" % (remote_path, vcs.get_default_revision()),
        shell=True,
    )
    check_call("cd %s && git checkout -b B3" % remote_path, shell=True)
    check_call(
        'cd %s && touch IPSUM && git add IPSUM && git commit -m "3rd branch"'
        % (remote_path,),
        shell=True,
    last_rev, previous_rev = _get_last_two_revisions("B3", revisions)
    assert_revision(last_rev, message="3rd branch", branches=["B3"])
    assert_revision(previous_rev, message="second branch commit", branches=["B2"])
    assert_revision(
        revisions[3], message="test", branches=[vcs.get_default_revision(), "B2", "B3"]
    )
    revisions = list(vcs.log(branch="B3"))
    assert_revision(revisions[0], message="3rd branch", branches=["B3"])
    assert_revision(
        revisions[2], message="test", branches=[vcs.get_default_revision(), "B2", "B3"]
    )
    check_call(
        "cd %s && git checkout %s" % (remote_path, vcs.get_default_revision()),
        shell=True,
    )
    revision = next(vcs.log(parent="HEAD", limit=1))
        revision,
        author="Foo Bar <foo@example.com>",
        message="biz\nbaz\n",
        subject="biz",
    assert revisions[0].subject == "biz"
    assert revisions[0].message == "biz\nbaz\n"
    assert revisions[0].author == "Foo Bar <foo@example.com>"
    assert revisions[0].committer == "Foo Bar <foo@example.com>"
    assert revisions[0].branches == ["master"]
    assert revisions[1].subject == "test"
    assert revisions[1].message == "test\nlol\n"
    assert revisions[1].author == "Foo Bar <foo@example.com>"
    assert revisions[1].committer == "Foo Bar <foo@example.com>"
    assert revisions[1].branches == ["master"]
    assert (
        diff
        == """diff --git a/BAR b/BAR
    )
    assert revisions[0].subject == "biz"
    assert revisions[0].subject == "test"
    assert (
        vcs.is_child_parent(
            child_in_question=revisions[1].sha, parent_in_question=revisions[0].sha
        )
        is False
    )
    assert "master" in branches
    check_call(
        "cd %s && git checkout -B test_branch" % git_repo_config.remote_path, shell=True
    )
    assert "test_branch" in branches
        'cd %s && echo "bar" > BAZ && git add BAZ && git commit -m "bazzy"'
        % git_repo_config.remote_path,
        shell=True,
    result = vcs.show(revisions[0].sha, "BAZ")
    assert result == "bar\n"