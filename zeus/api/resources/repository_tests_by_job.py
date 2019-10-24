from flask import current_app

from zeus.config import db
from zeus.constants import Result, Status
from zeus.models import Build, Repository, TestCase, Job, Source

from .base_repository import BaseRepositoryResource
from ..schemas import TestCaseSummarySchema

testcases_schema = TestCaseSummarySchema(many=True, strict=True)


class RepositoryTestsByJobResource(BaseRepositoryResource):
    def get(self, repo: Repository):
        """
        Return a list of testcases for the given repository.
        """
        # use the most recent successful build to fetch test results
        builds = (
            db.session.query(Build.id)
            .join(Source, Source.id == Build.source_id)
            .filter(
                Source.patch_id == None,  # NOQA
                Build.repository_id == repo.id,
                Build.result == Result.passed,
                Build.status == Status.finished,
            )
            .order_by(Build.number.asc())
            .limit(20)
        )

        if not builds:
            current_app.logger.info("no successful builds found for repository")
            return self.respond([])

        job_list = db.session.query(Job.id).filter(Job.build_id.in_(builds)).limit(30)

        if not job_list:
            current_app.logger.info("no successful jobs found for build")
            return self.respond([])

        query = TestCase.query.filter(TestCase.job_id.in_(job_list))

        results_by_test = {}

        for row in query.all():
            test_name = results_by_test.get(row.name, {})
            test_name[str(row.job_id)] = Result(row.result)
            results_by_test[row.name] = test_name

        jobs = list(map(lambda id: str(id[0]), job_list))

        results = {}
        for test_name, result_by_test in results_by_test.items():
            results[test_name] = []
            for job_id in jobs:
                results[test_name].insert(0, result_by_test.get(job_id, None))

        return self.respond(
            {"results": results, "results_by_test": results_by_test, "jobs": jobs}
        )
