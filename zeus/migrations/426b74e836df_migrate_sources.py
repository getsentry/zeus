"""migrate_sources

Revision ID: 426b74e836df
Revises: 070ac78ddbcb
Create Date: 2019-11-25 11:26:47.059916

"""
import sqlalchemy as sa

from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "426b74e836df"
down_revision = "070ac78ddbcb"
branch_labels = ()
depends_on = None

Build = sa.Table(
    "build",
    sa.MetaData(),
    sa.Column("id", postgresql.UUID(), primary_key=True),
    sa.Column("repository_id", postgresql.UUID()),
    sa.Column("author_id", postgresql.UUID()),
    sa.Column("source_id", postgresql.UUID()),
    sa.Column("ref", sa.String()),
    sa.Column("revision_sha", sa.String()),
)

Source = sa.Table(
    "source",
    sa.MetaData(),
    sa.Column("id", postgresql.UUID(), primary_key=True),
    sa.Column("repository_id", postgresql.UUID()),
    sa.Column("author_id", postgresql.UUID()),
    sa.Column("revision_sha", sa.String(length=40)),
)


def upgrade():
    connection = op.get_bind()
    for build in connection.execute(Build.select().where(Build.c.source_id != None)):
        source = next(
            connection.execute(Source.select().where(Source.c.id == Build.c.source_id))
        )
        connection.execute(
            Build.update()
            .where(Build.c.id == build.id)
            .values(
                author_id=source.author_id,
                ref=build.ref or build.revision_sha or source.revision_sha,
                revision_sha=build.revision_sha or source.revision_sha,
            )
        )


def downgrade():
    pass
