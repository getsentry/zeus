from flask import current_app

from zeus.config import db
from zeus.constants import Result, Status
from zeus.models import Build, Project, TestCase, Job, Source

from .base_project import BaseProjectResource
from ..schemas import TestCaseSummarySchema

testcases_schema = TestCaseSummarySchema(many=True, strict=True)


class ProjectTestsResource(BaseProjectResource):
    def get(self, project: Project):
        """
        Return a list of testcases for the given project.
        """
        latest_build = Build.query.join(
            Source,
            Source.id == Build.source_id,
        ).filter(
            Source.patch_id == None,  # NOQA
            Build.project_id == project.id,
            Build.result == Result.passed,
            Build.status == Status.finished,
        ).order_by(
            Build.date_created.desc(),
        ).first()

        if not latest_build:
            current_app.logger.info('no successful builds found for project')
            return self.respond([])

        job_list = db.session.query(Job.id).filter(
            Job.build_id == latest_build.id,
        )

        # use the most completed build to fetch test results
        query = TestCase.query.filter(
            TestCase.job_id.in_(job_list),
        )

        return self.respond_with_schema(testcases_schema, query)
