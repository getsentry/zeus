"""backfill_failure_build

Revision ID: 8ee8825cd590
Revises: 14f53101b654
Create Date: 2020-03-04 15:12:19.835756

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8ee8825cd590"
down_revision = "14f53101b654"
branch_labels = ()
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        update failurereason
        set build_id = (select build_id from job where job.id = failurereason.job_id)
        where build_id is null;
        """
    )


def downgrade():
    pass
