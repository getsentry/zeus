"""backfill_authors

Revision ID: 16414a5b4ed9
Revises: 56684708bb21
Create Date: 2020-01-07 16:21:35.504437

"""
import zeus
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "16414a5b4ed9"
down_revision = "56684708bb21"
branch_labels = ()
depends_on = None


def upgrade():
    connection = op.get_bind()

    connection.execute(
        """
        INSERT INTO build_author (build_id, author_id)
        SELECT id, author_id FROM build
        WHERE author_id IS NOT NULL
        ON CONFLICT DO NOTHING
        """
    )

    connection.execute(
        """
        INSERT INTO revision_author (repository_id, revision_sha, author_id)
        SELECT repository_id, sha, author_id FROM revision
        WHERE author_id IS NOT NULL
        ON CONFLICT DO NOTHING
        """
    )


def downgrade():
    pass
