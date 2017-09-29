"""job_allow_failures

Revision ID: 0d8163d0cfce
Revises: 53c5cd5b170f
Create Date: 2017-09-29 12:56:08.627724

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d8163d0cfce'
down_revision = '53c5cd5b170f'
branch_labels = ()
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('job', sa.Column('allow_failure', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('job', 'allow_failure')
    # ### end Alembic commands ###
