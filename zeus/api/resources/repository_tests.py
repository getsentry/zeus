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
                Job.repository_id == repo.id,
                Job.date_finished >= timezone.now() - timedelta(days=14),
                Job.status == Status.finished,
            )
            .group_by(TestCase.hash, TestCase.name)
            .order_by(runs_failed.desc())
        )

        return self.paginate_with_schema(testcases_schema, query)
