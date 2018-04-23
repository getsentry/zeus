from flask import Response
from sqlalchemy.orm import joinedload, undefer

from zeus.config import db
from zeus.models import TestCase

from .base import Resource
from ..schemas import TestCaseSchema

testcase_schema = TestCaseSchema(strict=True)


class TestDetailsResource(Resource):

    def dispatch_request(self, test_id: str, *args, **kwargs) -> Response:
        test = TestCase.query.options(undefer("message"), joinedload("job")).get(
            test_id
        )
        if not test:
            return self.not_found()

        return Resource.dispatch_request(self, test, *args, **kwargs)

    def get(self, test: TestCase):
        """
        Return a test.
        """
        return self.respond_with_schema(testcase_schema, test)

    def put(self, test: TestCase):
        """
        Update a test.
        """
        result = self.schema_from_request(testcase_schema, partial=True)
        if result.errors:
            return self.respond(result.errors, 403)

        for key, value in result.data.items():
            if getattr(test, key) != value:
                setattr(test, key, value)
        db.session.add(test)
        db.session.commit()
        return self.respond_with_schema(testcase_schema, test)
