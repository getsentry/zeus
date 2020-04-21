import os.path

from flask import current_app

from time import time
from uuid import UUID, uuid4

from zeus.exceptions import UnknownRepositoryBackend
from zeus.models import RepositoryBackend
from zeus.vcs.backends.base import Vcs, RevisionResult
from zeus.vcs.backends.git import GitVcs
from zeus.utils.sentry import span

CLEANUP_OPTION_NAME = "cleanup.last-run"


@span("get_author_id")
async def get_author_id(conn, repo_id: UUID, name: str, email: str) -> UUID:
    rv = await conn.fetch(
        """
        INSERT INTO author (id, repository_id, email, name)
        VALUES ($1::uuid, $2, $3, $4)
        ON CONFLICT DO NOTHING
        RETURNING id;
    """,
        str(uuid4()),
        repo_id,
        email,
        name,
    )
    if rv:
        return rv[0]["id"]
    return (
        await conn.fetch(
            """
        SELECT id FROM author WHERE repository_id = $1 AND email = $2 LIMIT 1
        """,
            repo_id,
            email,
        )
    )[0]["id"]


@span("save_revision")
async def save_revision(conn, repo_id: UUID, revision: RevisionResult):
    authors = revision.get_authors()

    async with conn.transaction():
        await conn.execute(
            """
            INSERT INTO revision (repository_id, sha, committer_id, message, parents, date_created, date_committed)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT DO NOTHING
        """,
            repo_id,
            revision.sha,
            await get_author_id(conn, repo_id, *revision.get_committer()),
            revision.message,
            revision.parents,
            revision.author_date,
            revision.committer_date,
        )
        for author in authors:
            await conn.execute(
                """
                INSERT INTO revision_author (repository_id, revision_sha, author_id)
                VALUES ($1, $2, $3)
                ON CONFLICT DO NOTHING
            """,
                repo_id,
                revision.sha,
                await get_author_id(conn, repo_id, *author),
            )


@span("get_vcs")
async def get_vcs(conn, repo_id: UUID) -> Vcs:
    repo = (
        await conn.fetch(
            """
        SELECT id, backend, url FROM repository WHERE id = $1
    """,
            repo_id,
        )
    )[0]
    options = dict(
        await conn.fetch(
            """
        SELECT name, value FROM itemoption WHERE id = $1 AND name IN ('auth.username')
    """,
            repo_id,
        )
    )

    kwargs = {
        "path": os.path.join(current_app.config["REPO_ROOT"], repo["id"].hex),
        "id": repo["id"].hex,
        "url": repo["url"],
        "username": options.get("auth.username"),
    }

    if repo["backend"] == RepositoryBackend.git:
        return GitVcs(**kwargs)

    raise UnknownRepositoryBackend("Invalid backend: {}".format(repo["backend"]))


@span("cleanup")
async def cleanup(conn, repo_id: UUID):
    vcs = await get_vcs(conn, repo_id)
    await vcs.cleanup()
    rv = await conn.fetch(
        """INSERT INTO itemoption (id, item_id, name, value)
    VALUES ($1::uuid, $2, $3, $4)
    ON CONFLICT DO NOTHING
    RETURNING id;""",
        str(uuid4()),
        repo_id,
        CLEANUP_OPTION_NAME,
        str(time()),
    )
    if rv:
        return
    await conn.fetch(
        "UPDATE itemoption SET value = $1 WHERE item_id = $2 AND name = $3 RETURNING id",
        str(time()),
        repo_id,
        CLEANUP_OPTION_NAME,
    )
