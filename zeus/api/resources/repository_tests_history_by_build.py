from collections import defaultdict
from flask import current_app, request
from marshmallow import Schema, fields, pre_dump

from zeus.config import db
from zeus.constants import Status
from zeus.models import Build, Repository, TestCase, Job

from .base_repository import BaseRepositoryResource
from ..schemas import ResultField, BuildSchema


class TestResultSchema(Schema):
    name = fields.Str(required=True)
    hash = fields.Str(dump_only=True)
    results = fields.List(ResultField)


class TestCaseHistorySchema(Schema):
    tests = fields.List(fields.Nested(TestResultSchema))
    builds = fields.List(
        fields.Nested(BuildSchema(exclude=["stats", "revision", "repository"]))
    )

    @pre_dump(pass_many=False)
    def process_results(self, data, **kwargs):
        testcase_query = (
            db.session.query(TestCase.hash, TestCase.result, Job.build_id)
            .join(Job, TestCase.job_id == Job.id)
            .filter(
                TestCase.hash.in_(n[1] for n in data),
                Job.build_id.in_(b.id for b in self.context["builds"]),
            )
        ).order_by(TestCase.name.asc())
        if self.context["query"]:
            testcase_query = testcase_query.filter(
                TestCase.name.contains(self.context["query"])
            )

        results_by_test = defaultdict(dict)
        for test_hash, result, build_id in testcase_query:
            results_by_test[test_hash][build_id] = result

        tests = []
        # XXX: looping on data to ensure we maintain order of original serialization
        for test_name, test_hash in data:
            tests.append(
                {
                    "name": test_name,
                    "hash": test_hash,
                    "results": [
                        results_by_test[test_hash].get(b.id, None)
                        for b in self.context["builds"]
                    ],
                }
            )

        output = {"tests": tests, "builds": self.context["builds"]}
        return output


class RepositoryTestsHistoryByBuildResource(BaseRepositoryResource):
    def get(self, repo: Repository):
        """
        Return a list of testcases for the given repository.
        """
        results = min(int(request.args.get("results", 20)), 100)
        query = request.args.get("query")

        builds = (
            Build.query.filter(
                Build.repository_id == repo.id, Build.status == Status.finished
            )
            .order_by(Build.number.desc())
            .limit(results)
        )

        if not builds:
            current_app.logger.info("no successful builds found for repository")
            return self.respond([])

        # this only fetches the unique test cases, as we need to paginate them
        testcase_query = (
            db.session.query(TestCase.name, TestCase.hash)
            .join(Job, TestCase.job_id == Job.id)
            .filter(Job.build_id.in_(b.id for b in builds))
            .distinct()
        )
        if query:
            testcase_query = testcase_query.filter(TestCase.name.contains(query))

        schema = TestCaseHistorySchema(context={"builds": builds, "query": query})

        return self.paginate_with_schema(schema, testcase_query)
