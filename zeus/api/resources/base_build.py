from flask import Response
from sqlalchemy.orm import contains_eager

from zeus.models import Build, Organization, Project

from .base import Resource


class BaseBuildResource(Resource):
    def dispatch_request(
        self, org_name: str, project_name: str, build_number: int, *args, **kwargs
    ) -> Response:
        build = Build.query.options(
            contains_eager('organization'),
            contains_eager('project'),
        ).join(Project, Project.id == Build.project_id).join(
            Organization, Project.organization_id == Organization.id
        ).filter(
            Organization.name == org_name,
            Project.name == project_name,
            Build.number == build_number,
        ).first()
        if not build:
            return self.not_found()
        return Resource.dispatch_request(self, build, *args, **kwargs)
