"""fix_source_constraint

Revision ID: 708db2afdda5
Revises: 6afba33703f5
Create Date: 2019-01-21 23:23:21.189099

"""
from alembic import op
import sqlalchemy as sa
import zeus

# revision identifiers, used by Alembic.
revision = "708db2afdda5"
down_revision = "6afba33703f5"
branch_labels = ()
depends_on = None

build_tbl = sa.sql.table("build", sa.sql.column("source_id", zeus.db.types.guid.GUID()))

source_tbl = sa.sql.table(
    "source",
    sa.sql.column("id", zeus.db.types.guid.GUID()),
    sa.sql.column("repository_id", zeus.db.types.guid.GUID()),
    sa.sql.column("revision_sha", sa.String(length=40)),
)


def upgrade():
    conn = op.get_bind()
    cursor = conn.execute(
        """
            select repository_id, revision_sha from source where patch_id is null group by repository_id, revision_sha having count(*) > 1
        """
    )
    results = cursor.fetchall()
    for repository_id, revision_sha in results:
        cursor2 = conn.execute(
            "select id from source where patch_id is null and repository_id = %s and revision_sha = %s",
            [repository_id, revision_sha],
        )
        dupes = cursor2.fetchall()
        valid_source_id = dupes[0][0]
        for (source_id,) in dupes[1:]:
            op.execute(
                build_tbl.update()
                .where(build_tbl.c.source_id == source_id)
                .values({"source_id": valid_source_id})
            )
            op.execute(source_tbl.delete().where(source_tbl.c.id == source_id))

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        "unq_source_revision2",
        "source",
        ["repository_id", "revision_sha"],
        unique=True,
        postgresql_where=sa.text("patch_id IS NULL"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("unq_source_revision2", table_name="source")
    # ### end Alembic commands ###
