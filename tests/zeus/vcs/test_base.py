from datetime import datetime

from zeus.models import Repository, Revision
from zeus.vcs.base import RevisionResult


def test_revision_result(db_session, default_repo: Repository):
    result = RevisionResult(
        sha="c" * 40,
        author="Foo Bar <foo@example.com>",
        committer="Biz Baz <baz@example.com>",
        author_date=datetime(2013, 9, 19, 22, 15, 22),
        committer_date=datetime(2013, 9, 19, 22, 15, 23),
        message="Hello world!",
        parents=["a" * 40, "b" * 40],
    )
    revision, created = result.save(default_repo)

    assert created

    assert type(revision) == Revision
    assert revision.repository_id == default_repo.id
    assert revision.sha == "c" * 40
    assert revision.message == "Hello world!"
    assert revision.author.name == "Foo Bar"
    assert revision.author.email == "foo@example.com"
    assert revision.committer.name == "Biz Baz"
    assert revision.committer.email == "baz@example.com"
    assert revision.parents == ["a" * 40, "b" * 40]
    assert revision.date_created == datetime(2013, 9, 19, 22, 15, 22)
    assert revision.date_committed == datetime(2013, 9, 19, 22, 15, 23)

    authors = {a.email: a.name for a in revision.authors}
    assert len(authors) == 1
    assert "foo@example.com" in authors

    # save it again for good measure
    revision, created = result.save(default_repo)


def test_revision_multiple_authors(db_session, default_repo: Repository):
    result = RevisionResult(
        sha="c" * 40,
        author="Foo Bar <foo@example.com>",
        committer="Biz Baz <baz@example.com>",
        author_date=datetime(2013, 9, 19, 22, 15, 22),
        committer_date=datetime(2013, 9, 19, 22, 15, 23),
        message="Hello world!\n\nCo-authored-by: Biz Baz <baz@example.com>\nCo-authored-by: Bar Foo <bar@example.com>",
        parents=["a" * 40, "b" * 40],
    )
    revision, created = result.save(default_repo)

    assert created

    assert type(revision) == Revision
    assert revision.repository_id == default_repo.id
    assert revision.sha == "c" * 40
    assert revision.author.name == "Foo Bar"
    assert revision.author.email == "foo@example.com"
    assert revision.committer.name == "Biz Baz"
    assert revision.committer.email == "baz@example.com"

    authors = {a.email: a.name for a in revision.authors}
    assert len(authors) == 3
    assert "foo@example.com" in authors
    assert "baz@example.com" in authors
    assert "bar@example.com" in authors

    # save it again for good measure
    revision, created = result.save(default_repo)
    authors = {a.email: a.name for a in revision.authors}
    assert len(authors) == 3
    assert "foo@example.com" in authors
    assert "baz@example.com" in authors
    assert "bar@example.com" in authors
