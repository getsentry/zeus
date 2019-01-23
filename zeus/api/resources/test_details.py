from sqlalchemy.orm import joinedload, undefer

from zeus.models import TestCase

from .base import Resource
from ..schemas import TestCaseSchema


class TestDetailsResource(Resource):
    def select_resource_for_update(self) -> bool:
        return False

    def get(self, test_id: str):
        testcase = TestCase.query.options(undefer("message"), joinedload("job")).get(
            test_id
        )

        schema = TestCaseSchema(strict=True)
        return self.respond_with_schema(schema, testcase)
