"""job_date_updated

Revision ID: bfe3af4f7eae
Revises: fe3baeb0605e
Create Date: 2017-11-15 15:27:07.022182

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bfe3af4f7eae"
down_revision = "fe3baeb0605e"
branch_labels = ()
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "job", sa.Column("date_updated", sa.TIMESTAMP(timezone=True), nullable=True)
    )


# ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("job", "date_updated")


# ### end Alembic commands ###
