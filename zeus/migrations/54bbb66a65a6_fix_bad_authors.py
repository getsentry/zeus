"""fix_bad_authors

Revision ID: 54bbb66a65a6
Revises: 52a5d85ba249
Create Date: 2020-03-10 14:40:53.336085

"""
from alembic import op
import logging
import sqlalchemy as sa

from uuid import uuid4

# revision identifiers, used by Alembic.
revision = "54bbb66a65a6"
down_revision = "52a5d85ba249"
branch_labels = ()
depends_on = None


def upgrade():
    connection = op.get_bind()

    authors = {}

    query = connection.execute(
        """
        SELECT a.id as old_id,
            a.name as email,
            a.email as name,
            a.repository_id,
            b.id as new_id
        FROM author AS a
        LEFT JOIN author AS b
        ON a.name = b.email
        AND a.repository_id = b.repository_id
        WHERE a.email NOT LIKE '%%@%%' AND a.name LIKE '%%@%%'
        """
    )
    for row in query.fetchall():
        old_id = row["old_id"]
        new_id = row["new_id"]

        with connection.begin_nested():
            logging.info(
                "Fixing author=%s - %s (%s)", old_id, row["name"], row["email"]
            )
            new_id = new_id or authors.get(row["email"])
            if not new_id:
                new_id = uuid4()
                connection.execute(
                    """
                    INSERT INTO author (id, repository_id, name, email)
                    VALUES (%s, %s, %s, %s)
                    """,
                    [new_id, row["repository_id"], row["name"], row["email"]],
                )
            connection.execute(
                """
                UPDATE revision_author
                SET author_id = %s
                WHERE author_id = %s
                AND NOT EXISTS (
                    SELECT 1 FROM revision_author WHERE author_id = %s
                )
                """,
                [new_id, old_id, new_id],
            )
            connection.execute(
                """
                UPDATE build_author
                SET author_id = %s
                WHERE author_id = %s
                AND NOT EXISTS (
                    SELECT 1 FROM build_author WHERE author_id = %s
                )
                """,
                [new_id, old_id, new_id],
            )
            connection.execute(
                """
                UPDATE change_request_author
                SET author_id = %s
                WHERE author_id = %s
                AND NOT EXISTS (
                    SELECT 1 FROM change_request_author WHERE author_id = %s
                )
                """,
                [new_id, old_id, new_id],
            )
            connection.execute(
                """
                DELETE FROM author
                WHERE id = %s
                """,
                [old_id],
            )
        authors[row["email"]] = new_id


def downgrade():
    pass
