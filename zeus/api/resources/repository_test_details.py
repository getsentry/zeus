from marshmallow import Schema, fields, pre_dump

from zeus.models import Build, Job, Repository, TestCase, TestCaseMeta
from zeus.api.schemas import BuildSchema

from .base_repository import BaseRepositoryResource


class TestCaseMetaSchema(Schema):
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
        last_build = (
            Build.query.join(Job, Job.build_id == Build.id)
            .join(TestCase, TestCase.job_id == Job.id)
            .filter(
                TestCase.repository_id == data.repository_id, TestCase.hash == data.hash
            )
            .order_by(TestCase.date_created.desc())
            .first()
        )

        return {
            "hash": data.hash,
            "name": data.name,
            "first_build": data.first_build,
            "last_build": last_build,
        }


class RepositoryTestDetailsResource(BaseRepositoryResource):
    def select_resource_for_update(self) -> bool:
        return False

    def get(self, repo: Repository, test_hash: str):
        testcase_meta = TestCaseMeta.query.filter(
            TestCaseMeta.repository_id == repo.id, TestCaseMeta.hash == test_hash
        ).first()
        if not testcase_meta:
            return self.respond({"message": "resource not found"}, 404)

        schema = TestCaseMetaSchema()
        return self.respond_with_schema(schema, testcase_meta)
