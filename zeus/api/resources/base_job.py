from flask import Response
from sqlalchemy.orm import contains_eager

from zeus.models import Build, Job, Organization, Project

from .base import Resource


class BaseJobResource(Resource):
    def dispatch_request(
        self, org_name: str, project_name: str, build_number: int, job_number: int, *args, **kwargs
    ) -> Response:
        job = Job.query.options(
            contains_eager('build'),
            contains_eager('organization'),
            contains_eager('project'),
        ).join(Build, Build.id == Job.build_id).join(Project, Project.id == Build.project_id).join(
            Organization,
            Organization.id == Project.organization_id,
        ).filter(
            Organization.name == org_name,
            Project.name == project_name,
            Build.number == build_number,
            Job.number == job_number,
        ).first()
        if not job:
            return self.not_found()

        return Resource.dispatch_request(self, job, *args, **kwargs)
