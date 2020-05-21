from datetime import timedelta
from sqlalchemy.sql import func

from zeus.config import db
from zeus.constants import Result, Status
from zeus.models import Repository, TestCase, Job
from zeus.utils import timezone

from .base_repository import BaseRepositoryResource
from ..schemas import TestCaseStatisticsSchema

testcases_schema = TestCaseStatisticsSchema(many=True)


class RepositoryTestsResource(BaseRepositoryResource):
    def get(self, repo: Repository):
        """
        Return a list of testcases for the given repository.
        """
        runs_failed = (
            func.count(TestCase.result)
            .filter(TestCase.result == Result.failed)
            .label("runs_failed")
        )

        repo_subquery = (
            db.session.query(Repository.id).filter(Repository.id == repo.id).subquery()
        )

        query = (
            db.session.query(
                TestCase.hash,
                TestCase.name,
                func.count(TestCase.hash).label("runs_total"),
                runs_failed,
                func.avg(TestCase.duration).label("avg_duration"),
            )
            .join(Job, Job.id == TestCase.job_id)
            .filter(
                # HACK(dcramer): we're working around the postgres 9.6 query planner refusing to use
                # our index here and doing a full sequence scan on testcase.. but only when the repository_id
                # is a fixed value
                Job.repository_id == repo_subquery,
                Job.date_finished >= timezone.now() - timedelta(days=14),
                Job.status == Status.finished,
            )
            .group_by(TestCase.hash, TestCase.name)
            .order_by(runs_failed.desc())
        )

        return self.paginate_with_schema(testcases_schema, query)
