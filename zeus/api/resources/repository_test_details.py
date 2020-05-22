from marshmallow import Schema, fields, pre_dump

from zeus.models import Build, Job, Repository, TestCase
from zeus.api.schemas import BuildSchema

from .base_repository import BaseRepositoryResource


class TestCaseSummarySchema(Schema):
    name = fields.Str(required=True)
    hash = fields.Str(dump_only=True)

    first_build = fields.Nested(
        BuildSchema(exclude=("repository", "revision", "stats")), required=False
    )
    last_build = fields.Nested(
        BuildSchema(exclude=("repository", "revision", "stats")), required=False
    )

    @pre_dump(pass_many=False)
    def process_testcase(self, data, many, **kwargs):
        first_build = (
            Build.query.join(Job, Job.build_id == Build.id)
            .join(TestCase, TestCase.job_id == Job.id)
            .filter(TestCase.hash == data.hash)
            .order_by(Job.date_created.asc())
            .first()
        )

        last_build = (
            Build.query.join(Job, Job.build_id == Build.id)
            .filter(Job.id == data.job_id)
            .order_by(Job.date_created.desc())
            .first()
        )

        return {
            "hash": data.hash,
            "name": data.name,
            "first_build": first_build,
            "last_build": last_build,
        }


class RepositoryTestDetailsResource(BaseRepositoryResource):
    def select_resource_for_update(self) -> bool:
        return False

    def get(self, repo: Repository, test_hash: str):
        testcase = (
            TestCase.query.filter(
                TestCase.repository_id == repo.id, TestCase.hash == test_hash
            )
            .join(TestCase.job)
            .order_by(Job.date_created.desc())
            .first()
        )

        schema = TestCaseSummarySchema()
        return self.respond_with_schema(schema, testcase)
