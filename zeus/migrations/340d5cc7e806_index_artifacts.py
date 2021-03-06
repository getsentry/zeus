"""index_artifacts

Revision ID: 340d5cc7e806
Revises: af3f4bdc27d1
Create Date: 2019-08-09 12:37:50.706914

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "340d5cc7e806"
down_revision = "af3f4bdc27d1"
branch_labels = ()
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        "idx_artifact_job", "artifact", ["repository_id", "job_id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("idx_artifact_job", table_name="artifact")
    # ### end Alembic commands ###
