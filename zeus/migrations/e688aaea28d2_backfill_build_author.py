"""backfill_build_author

Revision ID: e688aaea28d2
Revises: 523842e356fa
Create Date: 2018-10-01 13:20:10.394355

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e688aaea28d2"
down_revision = "523842e356fa"
branch_labels = ()
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        update build
        set author_id = (select author_id from source where build.source_id = source.id)
        where author_id is null;
        """
    )


def downgrade():
    pass
