"""backfill_cr_multi_author

Revision ID: 52a5d85ba249
Revises: 70383b887d4a
Create Date: 2020-03-04 15:23:10.842507

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "52a5d85ba249"
down_revision = "70383b887d4a"
branch_labels = ()
depends_on = None


def upgrade():
    connection = op.get_bind()

    connection.execute(
        """
        INSERT INTO change_request_author (change_request_id, author_id)
        SELECT id, author_id FROM change_request
        WHERE author_id IS NOT NULL
        ON CONFLICT DO NOTHING
        """
    )


def downgrade():
    pass
