"""migrate_github

Revision ID: 9dbc97018a55
Revises: f8013173ef21
Create Date: 2017-08-27 14:20:59.219862

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9dbc97018a55'
down_revision = 'f8013173ef21'
branch_labels = ()
depends_on = None


def upgrade():
    op.execute("update repository set provider = 'gh' where provider = 'github'")


def downgrade():
    op.execute("update repository set provider = 'github' where provider = 'gh'")
