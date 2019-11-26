"""fix_missing_metadata

Revision ID: 133fc1714306
Revises: 426b74e836df
Create Date: 2019-11-25 17:00:04.987915

"""
from alembic import op
from sqlalchemy.dialects import postgresql

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "133fc1714306"
down_revision = "426b74e836df"
branch_labels = ()
depends_on = None


Build = sa.Table(
    "build",
    sa.MetaData(),
    sa.Column("id", postgresql.UUID(), primary_key=True),
    sa.Column("repository_id", postgresql.UUID()),
    sa.Column("author_id", postgresql.UUID()),
    sa.Column("label", postgresql.UUID()),
    sa.Column("revision_sha", sa.String()),
)

Revision = sa.Table(
    "revision",
    sa.MetaData(),
    sa.Column("repository_id", postgresql.UUID()),
    sa.Column("sha", postgresql.UUID()),
    sa.Column("message", sa.String()),
    sa.Column("author_id", postgresql.UUID()),
)


def upgrade():
    connection = op.get_bind()
    for build in connection.execute(
        Build.select().where(
            sa.and_(Build.c.label == None, Build.c.revision_sha != None)
        )
    ):
        revision = next(
            connection.execute(
                Revision.select().where(
                    sa.and_(
                        Revision.c.repository_id == build.repository_id,
                        Revision.c.sha == build.revision_sha,
                    )
                )
            )
        )
        connection.execute(
            Build.update()
            .where(Build.c.id == build.id)
            .values(
                author_id=build.author_id or revision.author_id,
                label=build.label or revision.message.split("\n")[0],
            )
        )


def downgrade():
    pass
