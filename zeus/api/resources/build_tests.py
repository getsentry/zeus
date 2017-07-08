from sqlalchemy.orm import contains_eager

from zeus.models import Job, Build, TestCase

from .base import Resource
from ..schemas import TestCaseSchema

testcases_schema = TestCaseSchema(many=True, strict=True)


class BuildTestsResource(Resource):
    def get(self, build_id):
        """
        Return a list of test cases for a given build.
        """
        build = Build.query.get(build_id)
        if not build:
            return self.not_found()

        query = TestCase.query.options(contains_eager('job')).join(
            Job,
            TestCase.job_id == Job.id,
        ).filter(
            Job.build_id == build.id,
        )

        return self.respond_with_schema(testcases_schema, query)
