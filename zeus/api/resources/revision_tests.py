from flask import request
from sqlalchemy.dialects.postgresql import array_agg

from zeus.config import db
from zeus.constants import Result
from zeus.db.func import array_agg_row
from zeus.models import Job, TestCase, Revision
from zeus.utils.builds import fetch_build_for_revision

from .base_revision import BaseRevisionResource
from ..schemas import AggregateTestCaseSummarySchema


class RevisionTestsResource(BaseRevisionResource):
    def get(self, revision: Revision):
        """
        Return a list of test cases for a given revision.
        """
        build = fetch_build_for_revision(revision)
        if not build:
            return self.respond(status=404)

        build_ids = [original.id for original in build.original]

        job_query = db.session.query(Job.id).filter(Job.build_id.in_(build_ids))

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

        schema = AggregateTestCaseSummarySchema(many=True, exclude=("build",))
        return self.paginate_with_schema(schema, query)
