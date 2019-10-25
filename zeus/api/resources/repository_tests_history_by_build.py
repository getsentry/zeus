from collections import defaultdict
from flask import current_app, request
from marshmallow import Schema, fields, pre_dump

from zeus.config import db
from zeus.constants import Status
from zeus.models import Build, Repository, TestCase, Job, Source

from .base_repository import BaseRepositoryResource
from ..schemas import ResultField, BuildSchema


class TestCaseHistorySchema(Schema):
    results = fields.Dict(keys=fields.Str(), values=fields.List(ResultField))
    builds = fields.List(
        fields.Nested(BuildSchema(exclude=["stats", "source", "repository"]))
    )

    @pre_dump(pass_many=False)
    def process_results(self, data, **kwargs):
        results_by_test = defaultdict(dict)
        for test_name, result, build_id in data:
            results_by_test[test_name][build_id] = result

        results = {}
        for test_name, test_results in results_by_test.items():
            results[test_name] = []
            for build in self.context["builds"]:
                results[test_name].append(test_results.get(build.id, None))

        output = {"results": results, "builds": self.context["builds"]}
        return output


class RepositoryTestsHistoryByBuildResource(BaseRepositoryResource):
    def get(self, repo: Repository):
        """
        Return a list of testcases for the given repository.
        """
        results = min(int(request.args.get("results", 20)), 100)
        query = request.args.get("query")

        builds = (
            Build.query.join(Source, Source.id == Build.source_id)
            .filter(
                Source.patch_id == None,  # NOQA
                Build.repository_id == repo.id,
                Build.status == Status.finished,
            )
            .order_by(Build.number.desc())
            .limit(results)
        )

        if not builds:
            current_app.logger.info("no successful builds found for repository")
            return self.respond([])

        testcase_query = (
            db.session.query(TestCase.name, TestCase.result, Job.build_id)
            .join(Job, TestCase.job_id == Job.id)
            .filter(Job.build_id.in_(b.id for b in builds))
        )
        if query:
            testcase_query = testcase_query.filter(TestCase.name.contains(query))

        schema = TestCaseHistorySchema(context={"builds": builds})

        return self.paginate_with_schema(schema, testcase_query)
