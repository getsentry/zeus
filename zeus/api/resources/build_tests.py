from flask import request
from sqlalchemy.dialects.postgresql import array_agg

from zeus.config import db
from zeus.constants import Result
from zeus.db.func import array_agg_row
from zeus.models import Job, Build, TestCase

from .base_build import BaseBuildResource
from ..schemas import AggregateTestCaseSummarySchema

testcases_schema = AggregateTestCaseSummarySchema(many=True, strict=True)


class BuildTestsResource(BaseBuildResource):
    def get(self, build: Build):
        """
        Return a list of test cases for a given build.
        """
        job_query = db.session.query(Job.id).filter(Job.build_id == build.id)

        result = request.args.get("allowed_failures")
        if result == "false":
            job_query = job_query.filter(Job.allow_failure == False)  # NOQA
        job_ids = job_query.subquery()

        query = (
            db.session.query(
                TestCase.hash,
                TestCase.name,
                array_agg_row(
                    TestCase.id, TestCase.job_id, TestCase.duration, TestCase.result
                ).label("runs"),
            )
            .filter(TestCase.job_id.in_(job_ids))
            .group_by(TestCase.hash, TestCase.name)
        )

        result = request.args.get("result")
        if result:
            try:
                query = query.filter(TestCase.result == getattr(Result, result))
            except AttributeError:
                raise NotImplementedError

        query = query.order_by(
            (
                array_agg(TestCase.result).label("results").contains([Result.failed])
            ).desc(),
            TestCase.name.asc(),
        )

        return self.paginate_with_schema(testcases_schema, query)
