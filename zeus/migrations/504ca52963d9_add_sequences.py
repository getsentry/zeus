"""add_sequences

Revision ID: 504ca52963d9
Revises: 579ea2c4b9e3
Create Date: 2017-07-08 22:05:25.662064

"""
import zeus
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '504ca52963d9'
down_revision = '579ea2c4b9e3'
branch_labels = ()
depends_on = None

NEXT_ITEM_VALUE_FUNCTION = """
CREATE OR REPLACE FUNCTION next_item_value(uuid) RETURNS int AS $$
DECLARE
  cur_parent_id ALIAS FOR $1;
  next_value int;
BEGIN
  LOOP
    UPDATE itemsequence SET value = value + 1 WHERE parent_id = cur_parent_id
    RETURNING value INTO next_value;
    IF FOUND THEN
      RETURN next_value;
    END IF;

    BEGIN
        INSERT INTO itemsequence (parent_id, value) VALUES (cur_parent_id, 1)
        RETURNING value INTO next_value;
        RETURN next_value;
    EXCEPTION WHEN unique_violation THEN
        -- do nothing
    END;
  END LOOP;
END;
$$ LANGUAGE plpgsql
"""


def upgrade():
    op.create_table(
        'itemsequence',
        sa.Column('parent_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('value', sa.Integer(), server_default='0', nullable=False),
        sa.PrimaryKeyConstraint('parent_id', 'value')
    )
    op.add_column('build', sa.Column('number', sa.Integer(), nullable=False))
    op.create_unique_constraint('unq_build_number', 'build', ['repository_id', 'number'])
    op.add_column('job', sa.Column('number', sa.Integer(), nullable=False))
    op.create_unique_constraint('unq_job_number', 'job', ['build_id', 'number'])
    op.execute(NEXT_ITEM_VALUE_FUNCTION)


def downgrade():
    op.drop_constraint('unq_job_number', 'job', type_='unique')
    op.drop_column('job', 'number')
    op.drop_constraint('unq_build_number', 'build', type_='unique')
    op.drop_column('build', 'number')
    op.drop_table('itemsequence')
    op.execute('DROP FUNCTION IF EXISTS next_item_value(uuid)')
