"""backfill_testcase_rollup

Revision ID: 495c51627ec0
Revises: d05e8a773f11
Create Date: 2020-05-21 11:17:19.041610

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "495c51627ec0"
down_revision = "d05e8a773f11"
branch_labels = ()
depends_on = None


def upgrade():
    # XXX(dcramer): had to run this by hand in prod; keeping it here for posterity/documentation
    # conn = op.get_bind()
    # conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    # conn.execute(
    #     """
    #     INSERT INTO testcase_rollup (id, name, hash, repository_id, date, total_runs, total_duration, runs_passed, runs_failed)
    # (
    #     SELECT uuid_generate_v1(),
    #         t.name,
    #         t.hash,
    #         t.repository_id,
    #         j.date_finished::date as job_date,
    #         count(*), sum(duration),
    #         count(t.result) FILTER (WHERE t.result = 1) AS runs_passed,
    #         count(t.result) FILTER (WHERE t.result = 2) AS runs_failed
    #     FROM testcase t
    #     JOIN job j
    #     ON j.id = t.job_id
    #     GROUP BY t.name, t.hash, t.repository_id, job_date
    # )
    # ON CONFLICT (repository_id, hash, date) DO UPDATE
    # SET total_runs = EXCLUDED.total_runs,
    #     total_duration = EXCLUDED.total_duration,
    #     runs_passed = EXCLUDED.runs_passed,
    #     runs_failed = EXCLUDED.runs_failed;
    # """
    # )
    pass


def downgrade():
    pass
