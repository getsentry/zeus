"""unique_build_failures

Revision ID: e373a7bffa18
Revises: 54bbb66a65a6
Create Date: 2020-03-13 09:25:38.492704

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e373a7bffa18"
down_revision = "54bbb66a65a6"
branch_labels = ()
depends_on = None


def upgrade():
    # first we clean up duplicate rows
    connection = op.get_bind()
    connection.execute(
        """
        DELETE FROM failurereason a
        USING failurereason b
        WHERE a.id > b.id
        AND a.reason = b.reason
        AND a.build_id = b.build_id
        """
    )

    op.create_index(
        "unq_failurereason_buildonly",
        "failurereason",
        ["build_id", "reason"],
        unique=True,
        postgresql_where=sa.text("job_id IS NULL"),
    )


def downgrade():
    op.drop_index("unq_failurereason_buildonly", table_name="failurereason")
