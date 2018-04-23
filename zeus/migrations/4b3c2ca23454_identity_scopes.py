"""identity_scopes

Revision ID: 4b3c2ca23454
Revises: c257bd5a6236
Create Date: 2017-10-11 11:40:44.554528

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "4b3c2ca23454"
down_revision = "c257bd5a6236"
branch_labels = ()
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "identity",
        sa.Column("scopes", postgresql.ARRAY(sa.String(length=64)), nullable=True),
    )


# ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("identity", "scopes")


# ### end Alembic commands ###
