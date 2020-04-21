from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import UUID

from zeus.vcs.backends.base import RevisionResult
from zeus.vcs.utils import cleanup, get_vcs, save_revision


async def test_get_vcs(vcs_db, default_repo_id: UUID):
    vcs = await get_vcs(vcs_db, default_repo_id)
    assert vcs.url == "https://github.com/getsentry/zeus.git"


async def test_save_revision(vcs_db, default_repo_id: UUID):
    result = RevisionResult(
        sha="c" * 40,
        author="Foo Bar <foo@example.com>",
        committer="Biz Baz <baz@example.com>",
        author_date=datetime(2013, 9, 19, 22, 15, 22, tzinfo=timezone.utc),
        committer_date=datetime(2013, 9, 19, 22, 15, 23, tzinfo=timezone.utc),
        message="Hello world!",
        parents=["a" * 40, "b" * 40],
    )

    await save_revision(vcs_db, default_repo_id, result)

    revision = (
        await vcs_db.fetch(
            """
            SELECT committer_id, message, parents, date_created, date_committed
            FROM revision
            WHERE sha = $1 AND repository_id = $2
            LIMIT 1
        """,
            "c" * 40,
            default_repo_id,
        )
    )[0]

    assert revision["message"] == "Hello world!"
    assert revision["parents"] == ["a" * 40, "b" * 40]
    assert revision["date_created"] == datetime(
        2013, 9, 19, 22, 15, 22, tzinfo=timezone.utc
    )
    assert revision["date_committed"] == datetime(
        2013, 9, 19, 22, 15, 23, tzinfo=timezone.utc
    )

    committer = (
        await vcs_db.fetch(
            """
            SELECT name, email
            FROM author
            WHERE id = $1 AND repository_id = $2
            LIMIT 1
        """,
            revision["committer_id"],
            default_repo_id,
        )
    )[0]
    assert committer["name"] == "Biz Baz"
    assert committer["email"] == "baz@example.com"

    authors = {
        a["email"]: a["name"]
        for a in (
            await vcs_db.fetch(
                """
            SELECT a.name, a.email
            FROM revision_author as ra
            JOIN author as a
            ON a.id = ra.author_id
            WHERE ra.revision_sha = $1 AND ra.repository_id = $2
        """,
                "c" * 40,
                default_repo_id,
            )
        )
    }
    assert len(authors) == 1
    assert "foo@example.com" in authors

    # TODO(dcramer): the way we patch sqla for pytest doesnt allow for this to work
    # save it again for good measure
    await save_revision(vcs_db, default_repo_id, result)


async def test_revision_multiple_authors(vcs_db, default_repo_id: UUID):
    result = RevisionResult(
        sha="c" * 40,
        author="Foo Bar <foo@example.com>",
        committer="Biz Baz <baz@example.com>",
        author_date=datetime(2013, 9, 19, 22, 15, 22, tzinfo=timezone.utc),
        committer_date=datetime(2013, 9, 19, 22, 15, 23, tzinfo=timezone.utc),
        message="Hello world!\n\nCo-authored-by: Biz Baz <baz@example.com>\nCo-authored-by: Bar Foo <bar@example.com>",
        parents=["a" * 40, "b" * 40],
    )

    await save_revision(vcs_db, default_repo_id, result)

    revision = (
        await vcs_db.fetch(
            """
            SELECT committer_id, message, parents, date_created, date_committed
            FROM revision
            WHERE sha = $1 AND repository_id = $2
            LIMIT 1
        """,
            "c" * 40,
            default_repo_id,
        )
    )[0]

    assert (
        revision["message"]
        == "Hello world!\n\nCo-authored-by: Biz Baz <baz@example.com>\nCo-authored-by: Bar Foo <bar@example.com>"
    )
    assert revision["parents"] == ["a" * 40, "b" * 40]
    assert revision["date_created"] == datetime(
        2013, 9, 19, 22, 15, 22, tzinfo=timezone.utc
    )
    assert revision["date_committed"] == datetime(
        2013, 9, 19, 22, 15, 23, tzinfo=timezone.utc
    )

    committer = (
        await vcs_db.fetch(
            """
            SELECT name, email
            FROM author
            WHERE id = $1 AND repository_id = $2
            LIMIT 1
        """,
            revision["committer_id"],
            default_repo_id,
        )
    )[0]
    assert committer["name"] == "Biz Baz"
    assert committer["email"] == "baz@example.com"

    authors = {
        a["email"]: a["name"]
        for a in (
            await vcs_db.fetch(
                """
            SELECT a.name, a.email
            FROM revision_author as ra
            JOIN author as a
            ON a.id = ra.author_id
            WHERE ra.revision_sha = $1 AND ra.repository_id = $2
        """,
                "c" * 40,
                default_repo_id,
            )
        )
    }
    assert len(authors) == 3
    assert "foo@example.com" in authors
    assert "baz@example.com" in authors
    assert "bar@example.com" in authors

    # TODO(dcramer): the way we patch sqla for pytest doesnt allow for this to work
    # save it again for good measure
    await save_revision(vcs_db, default_repo_id, result)


async def test_cleanup(mocker, vcs_db, default_repo_id: UUID):
    vcs_cleanup = mocker.patch("zeus.vcs.backends.git.GitVcs.cleanup", AsyncMock())

    await cleanup(vcs_db, default_repo_id)

    vcs_cleanup.assert_called_once_with()

    result = await vcs_db.fetch(
        """
            SELECT value FROM itemoption WHERE name = 'cleanup.last-run' AND item_id = $1
        """,
        default_repo_id,
    )
    assert result

    # run it again and ensure its updated (also tests UPDATE vs INSERT path)
    await cleanup(vcs_db, default_repo_id)

    result2 = await vcs_db.fetch(
        """
            SELECT value FROM itemoption WHERE name = 'cleanup.last-run' AND item_id = $1
        """,
        default_repo_id,
    )
    assert result2 > result
