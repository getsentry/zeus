from zeus.config import db
from zeus.models import Organization, Project

from .base_organization import BaseOrganizationResource
from ..schemas import ProjectSchema

project_schema = ProjectSchema(strict=True)
projects_schema = ProjectSchema(many=True, strict=True)


class OrganizationProjectsResource(BaseOrganizationResource):
    def get(self, org: Organization):
        """
        Return a list of projects.
        """
        query = Project.query.filter(
            Project.organization_id == org.id,
        )
        return self.respond_with_schema(projects_schema, query)

    def post(self, org: Organization):
        result = self.schema_from_request(project_schema)
        if result.errors:
            return self.respond(result.errors, 403)
        data = result.data
        project = Project(organization_id=org.id, **data)
        db.session.add(project)
        db.session.commit()

        return self.respond_with_schema(project_schema, project)
