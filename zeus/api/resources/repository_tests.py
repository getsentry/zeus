from flask import current_app

from zeus.config import db
from zeus.constants import Result, Status
from zeus.models import Build, Repository, TestCase, Job, Source

from .base_repository import BaseRepositoryResource
from ..schemas import TestCaseSummarySchema

testcases_schema = TestCaseSummarySchema(many=True, strict=True)


class RepositoryTestsResource(BaseRepositoryResource):
    def get(self, repo: Repository):
        """
        Return a list of testcases for the given repository.
        """
        # use the most recent successful build to fetch test results
        latest_build = Build.query.join(
            Source,
            Source.id == Build.source_id,
        ).filter(
            Source.patch_id == None,  # NOQA
            Build.repository_id == repo.id,
            Build.result == Result.passed,
            Build.status == Status.finished,
        ).order_by(
            Build.number.desc(),
        ).first()

        if not latest_build:
            current_app.logger.info('no successful builds found for repository')
            return self.respond([])

        job_list = db.session.query(Job.id).filter(
            Job.build_id == latest_build.id,
        )
        if not job_list:
            current_app.logger.info('no successful jobs found for build')
            return self.respond([])

        query = TestCase.query.filter(
            TestCase.job_id.in_(job_list),
        )

        return self.paginate_with_schema(testcases_schema, query)
