from flask import request
from sqlalchemy.orm import contains_eager

from zeus.constants import Result
from zeus.models import Job, TestCase, Revision
from zeus.utils.builds import fetch_build_for_revision

from .base_revision import BaseRevisionResource
from ..schemas import TestCaseSummarySchema

testcases_schema = TestCaseSummarySchema(many=True, strict=True)


class RevisionTestsResource(BaseRevisionResource):
    def get(self, revision: Revision):
        """
        Return a list of test cases for a given revision.
        """
        build = fetch_build_for_revision(revision.repository, revision)
        build_ids = [original.id for original in build.original]
        query = TestCase.query.options(contains_eager('job')).join(
            Job,
            TestCase.job_id == Job.id,
        ).filter(
            Job.build_id.in_(build_ids),
        )

        result = request.args.get('result')
        if result:
            try:
                query = query.filter(
                    TestCase.result == getattr(Result, result))
            except AttributeError:
                raise NotImplementedError

        query = query.order_by(
            (TestCase.result == Result.failed).desc(), TestCase.name.asc())

        return self.paginate_with_schema(testcases_schema, query)
