"""add_refs

Revision ID: 8536b0fcf0a2
Revises: 1782e8a9f689
Create Date: 2019-11-22 11:50:53.872660

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "8536b0fcf0a2"
down_revision = "1782e8a9f689"
branch_labels = ()
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("build", sa.Column("ref", sa.String(), nullable=True))
    op.add_column(
        "build", sa.Column("revision_sha", sa.String(length=40), nullable=True)
    )
    op.alter_column(
        "build", "source_id", existing_type=postgresql.UUID(), nullable=True
    )
    op.create_index(
        "idx_build_repo_sha", "build", ["repository_id", "revision_sha"], unique=False
    )
    op.create_foreign_key(
        None,
        "build",
        "revision",
        ["repository_id", "revision_sha"],
        ["repository_id", "sha"],
    )
    op.add_column("change_request", sa.Column("head_ref", sa.String(), nullable=True))
    op.add_column("change_request", sa.Column("parent_ref", sa.String(), nullable=True))
    op.alter_column(
        "change_request",
        "parent_revision_sha",
        existing_type=sa.VARCHAR(length=40),
        nullable=True,
    )
    op.add_column("patch", sa.Column("parent_ref", sa.String(), nullable=True))
    op.alter_column(
        "patch",
        "parent_revision_sha",
        existing_type=sa.VARCHAR(length=40),
        nullable=True,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "patch",
        "parent_revision_sha",
        existing_type=sa.VARCHAR(length=40),
        nullable=False,
    )
    op.drop_column("patch", "parent_ref")
    op.alter_column(
        "change_request",
        "parent_revision_sha",
        existing_type=sa.VARCHAR(length=40),
        nullable=False,
    )
    op.drop_column("change_request", "parent_ref")
    op.drop_column("change_request", "head_ref")
    op.drop_constraint(None, "build", type_="foreignkey")
    op.drop_index("idx_build_repo_sha", table_name="build")
    op.alter_column(
        "build", "source_id", existing_type=postgresql.UUID(), nullable=False
    )
    op.drop_column("build", "revision_sha")
    op.drop_column("build", "ref")
    # ### end Alembic commands ###
