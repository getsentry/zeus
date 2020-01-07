"""backfill_authors

Revision ID: 16414a5b4ed9
Revises: 56684708bb21
Create Date: 2020-01-07 16:21:35.504437

"""
import zeus
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "16414a5b4ed9"
down_revision = "56684708bb21"
branch_labels = ()
depends_on = None

Build = sa.Table(
    "build",
    sa.MetaData(),
    sa.Column("id", zeus.db.types.guid.GUID(), primary_key=True),
    sa.Column("author_id", zeus.db.types.guid.GUID()),
)

BuildAuthor = sa.Table(
    "build_author",
    sa.MetaData(),
    sa.Column("build_id", zeus.db.types.guid.GUID(), primary_key=True),
    sa.Column("author_id", zeus.db.types.guid.GUID(), primary_key=True),
)


Revision = sa.Table(
    "revision",
    sa.MetaData(),
    sa.Column("repository_id", zeus.db.types.guid.GUID(), primary_key=True),
    sa.Column("sha", sa.String(40), primary_key=True),
    sa.Column("author_id", zeus.db.types.guid.GUID()),
)

RevisionAuthor = sa.Table(
    "revision_author",
    sa.MetaData(),
    sa.Column("repository_id", zeus.db.types.guid.GUID(), primary_key=True),
    sa.Column("revision_sha", sa.String(40), primary_key=True),
    sa.Column("author_id", zeus.db.types.guid.GUID(), primary_key=True),
)


def upgrade():
    connection = op.get_bind()
    for build in connection.execute(Build.select()):
        connection.execute(
            BuildAuthor.insert().values(build_id=build.id, author_id=build.author_id)
        )

    for revision in connection.execute(Revision.select()):
        connection.execute(
            """
            INSERT INTO revision_author (repository_id, revision_sha, author_id)
            SELECT repository_id, sha, author_id FROM revision
            ON CONFLICT DO NOTHING
            """
        )


def downgrade():
    pass
