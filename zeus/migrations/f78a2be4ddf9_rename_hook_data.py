"""rename_hook_data

Revision ID: f78a2be4ddf9
Revises: d84e557ec8f6
Create Date: 2018-01-12 09:04:17.878406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f78a2be4ddf9'
down_revision = 'd84e557ec8f6'
branch_labels = ()
depends_on = None


def upgrade():
    op.alter_column('hook', 'data', new_column_name='config')


def downgrade():
    op.alter_column('hook', 'config', new_column_name='data')
