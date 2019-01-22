from flask import request
from sqlalchemy.dialects.postgresql import array_agg

from zeus.config import db
from zeus.constants import Result
from zeus.db.func import array_agg_row
from zeus.models import Job, Build, Repository, TestCase

from .base_repository import BaseRepositoryResource
from ..schemas import AggregateTestCaseSummarySchema


class TestHistoryResource(BaseRepositoryResource):
    def select_resource_for_update(self) -> bool:
        return False

    def get(self, repo: Repository, test_hash: str):
        query = (
            db.session.query(
                Build.id.label("build_id"),
                TestCase.hash,
                TestCase.name,
                array_agg_row(
                    TestCase.id, TestCase.job_id, TestCase.duration, TestCase.result
                ).label("runs"),
            )
            # .join(Job, Job.id == TestCase.job_id)
            # .join(Build, Build.id == Job.build_id)
            .filter(
                TestCase.hash == test_hash,
                TestCase.repository_id == repo.id,
                Build.id == Job.build_id,
                Job.id == TestCase.job_id,
            ).group_by(Build.id, TestCase.hash, TestCase.name)
        )

        result = request.args.get("result")
        if result:
            try:
                query = query.filter(TestCase.result == getattr(Result, result))
            except AttributeError:
                raise NotImplementedError

        query = query.order_by(
            Build.id,
            (
                array_agg(TestCase.result).label("results").contains([Result.failed])
            ).desc(),
            TestCase.name.asc(),
        )

        schema = AggregateTestCaseSummarySchema(
            many=True, strict=True, context={"repo": repo}
        )
        return self.paginate_with_schema(schema, query)
