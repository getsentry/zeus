from sqlalchemy.orm import contains_eager, undefer
from zeus.models import Build, Job, TestCase

from .base_build import BaseBuildResource
from ..schemas import TestCaseSchema

testcase_schema = TestCaseSchema(strict=True)


class TestDetailsResource(BaseBuildResource):
    def get(self, build: Build, test_name: str):
        """
        Return a test.
        """
        test = TestCase.query.options(contains_eager('job'), undefer('message')).join(
            Job,
            TestCase.job_id == Job.id,
        ).filter(
            Job.build_id == build.id,
            TestCase.name == test_name,
        ).first()
        if not test:
            return self.not_found()
        return self.respond_with_schema(testcase_schema, test)
