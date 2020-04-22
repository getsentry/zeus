"""index_finished_jobs

Revision ID: 392eb568af84
Revises: e373a7bffa18
Create Date: 2020-04-22 12:59:25.815399

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "392eb568af84"
down_revision = "e373a7bffa18"
branch_labels = ()
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        "idx_job_finished",
        "job",
        ["repository_id", "status", "date_finished"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("idx_job_finished", table_name="job")
    # ### end Alembic commands ###
