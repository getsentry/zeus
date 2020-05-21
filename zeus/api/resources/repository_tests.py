from datetime import timedelta
from sqlalchemy.sql import func

from zeus.config import db
from zeus.models import Repository, TestCaseRollup
from zeus.utils import timezone

from .base_repository import BaseRepositoryResource
from ..schemas import TestCaseStatisticsSchema

testcases_schema = TestCaseStatisticsSchema(many=True)


class RepositoryTestsResource(BaseRepositoryResource):
    def get(self, repo: Repository):
        """
        Return a historical view of testcase results for the given repository.
        """

        runs_failed = func.sum(TestCaseRollup.runs_failed).label("runs_failed")

        query = (
            db.session.query(
                TestCaseRollup.hash,
                TestCaseRollup.name,
                func.sum(TestCaseRollup.total_runs).label("total_runs"),
                runs_failed,
                (
                    func.sum(TestCaseRollup.total_duration)
                    / func.sum(TestCaseRollup.total_runs)
                ).label("avg_duration"),
            )
            .filter(
                # HACK(dcramer): we're working around the postgres 9.6 query planner refusing to use
                # our index here and doing a full sequence scan on testcase.. but only when the repository_id
                # is a fixed value
                TestCaseRollup.repository_id == repo.id,
                TestCaseRollup.date >= timezone.now() - timedelta(days=30),
            )
            .group_by(TestCaseRollup.hash, TestCaseRollup.name)
            .order_by(runs_failed.desc())
        )

        return self.paginate_with_schema(testcases_schema, query)
