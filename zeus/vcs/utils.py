import os.path

from flask import current_app
from uuid import uuid4

from zeus.exceptions import UnknownRepositoryBackend
from zeus.models import RepositoryBackend
from zeus.vcs.backends.git import GitVcs


async def get_author_id(db, repo_id: str, email: str, name: str):
    rv = await db.fetch(
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
        return rv[0]
    return (
        await db.fetch(
            """
        SELECT id FROM author WHERE repository_id = $1 AND email = $2 LIMIT 1
        """,
            repo_id,
            email,
        )
    )[0]


async def save_revision(db, repo_id, revision):
    authors = revision.get_authors()

    tr = await db.transaction()
    await tr.start()
    try:
        await db.execute(
            """
            INSERT INTO revision (repository_id, sha, author_id, committer_id, message, parents, branches, date_created, date_committed)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT DO NOTHING
        """,
            repo_id,
            revision.sha,
            (await get_author_id(db, repo_id, *authors[0]))["id"],
            (await get_author_id(db, repo_id, *revision.get_committer()))["id"],
            revision.message,
            revision.parents,
            revision.branches,
            revision.author_date,
            revision.committer_date,
        )
        for author in authors:
            await db.execute(
                """
                INSERT INTO revision_author (repository_id, revision_sha, author_id)
                VALUES ($1, $2, $3)
                ON CONFLICT DO NOTHING
            """,
                repo_id,
                revision.sha,
                (await get_author_id(db, repo_id, *author))["id"],
            )
    except Exception:
        await tr.rollback()
        raise
    else:
        await tr.commit()


async def get_vcs(app, repo_id):
    db = app["db"]
    repo = (
        await db.fetch(
            """
        SELECT id, backend, url FROM repository WHERE id = $1
    """,
            repo_id,
        )
    )[0]
    options = dict(
        await db.fetch(
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
