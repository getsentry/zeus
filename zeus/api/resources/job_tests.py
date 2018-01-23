from flask import request
from sqlalchemy.exc import IntegrityError

from zeus.config import db
from zeus.constants import Result
from zeus.models import Job, TestCase

from .base_job import BaseJobResource
from ..schemas import TestCaseSummarySchema

testcase_schema = TestCaseSummarySchema(strict=True, exclude=['job'])
testcases_schema = TestCaseSummarySchema(
    many=True, strict=True, exclude=['job'])


class JobTestsResource(BaseJobResource):
    def select_resource_for_update(self):
        return False

    def get(self, job: Job):
        """
        Return a list of test cases for a given job.
        """
        query = TestCase.query.filter(
            TestCase.job_id == job.id,
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

        return self.respond_with_schema(testcases_schema, query)

    def post(self, job: Job):
        """
        Create or overwrite a test. Generally used for streaming test results one at a time.
        """
        result = self.schema_from_request(testcase_schema)
        if result.errors:
            return self.respond(result.errors, 403)
        try:
            with db.session.begin_nested():
                test = TestCase(repository_id=job.repository_id,
                                job_id=job.id, **result.data)
                db.session.add(test)
            status = 201
        except IntegrityError:
            test = TestCase.query.filter(
                TestCase.repository_id == job.repository_id,
                TestCase.job_id == job.id,
                TestCase.name == result.data['name'],
            ).first()
            assert test
            for key, value in result.data.items():
                if getattr(test, key) != value:
                    setattr(test, key, value)
            if db.session.is_modified(test):
                db.session.add(test)
                db.session.commit()
                status = 202
            else:
                status = 200
        return self.respond_with_schema(testcase_schema, test, status)
