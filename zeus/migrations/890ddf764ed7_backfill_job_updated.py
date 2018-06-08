"""backfill_job_updated

Revision ID: 890ddf764ed7
Revises: bfe3af4f7eae
Create Date: 2017-11-15 15:29:56.970335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "890ddf764ed7"
down_revision = "bfe3af4f7eae"
branch_labels = ()
depends_on = None

Job = sa.Table(
    "job",
    sa.MetaData(),
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("date_created", sa.TIMESTAMP(timezone=True)),
    sa.Column("date_updated", sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column("date_finished", sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column("date_started", sa.TIMESTAMP(timezone=True), nullable=True),
)


def upgrade():
    connection = op.get_bind()
    for job in connection.execute(Job.select().where(Job.c.date_updated == None)):
        connection.execute(
            Job.update()
            .where(Job.c.id == job.id)
            .values(
                date_updated=job.date_finished or job.date_started or job.date_created
            )
        )


def downgrade():
    pass
