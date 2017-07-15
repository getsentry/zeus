from flask import Response
from sqlalchemy.orm import contains_eager

from zeus.models import Organization, Project

from .base import Resource


class BaseProjectResource(Resource):
    def dispatch_request(self, org_name: str, project_name: str, *args, **kwargs) -> Response:
        project = Project.query.options(
            contains_eager('organization'),
        ).join(
            Organization,
            Organization.id == Project.organization_id,
        ).filter(
            Organization.name == org_name,
            Project.name == project_name,
        ).first()
        if not project:
            return self.not_found()
        return Resource.dispatch_request(self, project, *args, **kwargs)
