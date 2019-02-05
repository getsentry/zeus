"""fix_source_constraint

Revision ID: 404ac069de83
Revises: 708db2afdda5
Create Date: 2019-01-21 23:26:11.736521

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "404ac069de83"
down_revision = "708db2afdda5"
branch_labels = ()
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        "unq_source_revision3",
        "source",
        ["repository_id", "revision_sha", "patch_id"],
        unique=True,
        postgresql_where=sa.text("patch_id IS NOT NULL"),
    )
    op.drop_constraint("unq_source_revision", "source", type_="unique")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(
        "unq_source_revision", "source", ["repository_id", "revision_sha", "patch_id"]
    )
    op.drop_index("unq_source_revision3", table_name="source")
    # ### end Alembic commands ###