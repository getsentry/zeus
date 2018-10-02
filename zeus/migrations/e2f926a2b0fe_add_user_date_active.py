"""add_user_date_active

Revision ID: e2f926a2b0fe
Revises: e688aaea28d2
Create Date: 2018-10-01 16:25:03.031284

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e2f926a2b0fe"
down_revision = "e688aaea28d2"
branch_labels = ()
depends_on = None


def upgrade():
    op.add_column(
        "user",
        sa.Column(
            "date_active",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(op.f("ix_user_date_active"), "user", ["date_active"], unique=False)
    connection = op.get_bind()
    connection.execute(
        """
        update "user" set date_active = date_created
        """
    )


def downgrade():
    op.drop_index(op.f("ix_user_date_active"), table_name="user")
    op.drop_column("user", "date_active")
