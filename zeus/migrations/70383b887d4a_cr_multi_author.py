"""cr_multi_author

Revision ID: 70383b887d4a
Revises: 8ee8825cd590
Create Date: 2020-03-04 15:21:40.180785

"""
import zeus
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "70383b887d4a"
down_revision = "8ee8825cd590"
branch_labels = ()
depends_on = None


def upgrade():
    op.create_table(
        "change_request_author",
        sa.Column("change_request_id", zeus.db.types.guid.GUID(), nullable=False),
        sa.Column("author_id", zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["author.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["change_request_id"], ["change_request.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("change_request_id", "author_id"),
    )


def downgrade():
    op.drop_table("change_request_author")
