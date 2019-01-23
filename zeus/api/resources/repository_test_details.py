from sqlalchemy.orm import contains_eager

from zeus.models import Job, Repository, TestCase

from .base_repository import BaseRepositoryResource
from ..schemas import TestCaseSummarySchema


class RepositoryTestDetailsResource(BaseRepositoryResource):
    def select_resource_for_update(self) -> bool:
        return False

    def get(self, repo: Repository, test_hash: str):
        testcase = (
            TestCase.query.filter(
                TestCase.repository_id == repo.id, TestCase.hash == test_hash
            )
            .join(TestCase.job)
            .options(contains_eager("job"))
            .order_by(Job.date_created.desc())
            .first()
        )

        schema = TestCaseSummarySchema(strict=True)
        return self.respond_with_schema(schema, testcase)
