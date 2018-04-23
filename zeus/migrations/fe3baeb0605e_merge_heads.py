"""merge heads

Revision ID: fe3baeb0605e
Revises: b3eb342cfd7e, 9d374079e8fc
Create Date: 2017-11-15 15:26:40.975005

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fe3baeb0605e"
down_revision = ("b3eb342cfd7e", "9d374079e8fc")
branch_labels = ()
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
