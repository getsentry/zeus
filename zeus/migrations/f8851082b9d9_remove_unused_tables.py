"""remove_unused_tables

Revision ID: f8851082b9d9
Revises: 483a30c028ec
Create Date: 2020-01-06 15:23:52.042899

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f8851082b9d9"
down_revision = "483a30c028ec"
branch_labels = ()
depends_on = None


def upgrade():
    op.drop_table("source")
    op.drop_table("patch")


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "source",
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("patch_id", postgresql.UUID(), autoincrement=False, nullable=True),
        sa.Column(
            "revision_sha", sa.VARCHAR(length=40), autoincrement=False, nullable=False
        ),
        sa.Column(
            "date_created",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("data", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "repository_id", postgresql.UUID(), autoincrement=False, nullable=False
        ),
        sa.Column("author_id", postgresql.UUID(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["author.id"],
            name="source_author_id_fkey",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["patch_id"], ["patch.id"], name="source_patch_id_fkey", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["repository_id", "revision_sha"],
            ["revision.repository_id", "revision.sha"],
            name="source_repository_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repository.id"],
            name="source_repository_id_fkey1",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="source_pkey"),
        sa.UniqueConstraint("patch_id", name="source_patch_id_key"),
    )
    op.create_index(
        "unq_source_revision3",
        "source",
        ["repository_id", "revision_sha", "patch_id"],
        unique=True,
    )
    op.create_index(
        "unq_source_revision2", "source", ["repository_id", "revision_sha"], unique=True
    )
    op.create_index(
        "ix_source_repository_id", "source", ["repository_id"], unique=False
    )
    op.create_index("ix_source_author_id", "source", ["author_id"], unique=False)
    op.create_index(
        "idx_source_repo_sha", "source", ["repository_id", "revision_sha"], unique=False
    )
    op.create_table(
        "patch",
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            "parent_revision_sha",
            sa.VARCHAR(length=40),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("diff", sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column(
            "date_created",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "repository_id", postgresql.UUID(), autoincrement=False, nullable=False
        ),
        sa.Column("parent_ref", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["repository_id", "parent_revision_sha"],
            ["revision.repository_id", "revision.sha"],
            name="patch_repository_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repository.id"],
            name="patch_repository_id_fkey1",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="patch_pkey"),
    )
    op.create_index("ix_patch_repository_id", "patch", ["repository_id"], unique=False)
    op.create_index(
        "idx_repo_sha", "patch", ["repository_id", "parent_revision_sha"], unique=False
    )
    # ### end Alembic commands ###
