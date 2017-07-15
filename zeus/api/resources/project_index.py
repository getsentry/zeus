from sqlalchemy.orm import joinedload

from zeus.models import Project

from .base import Resource
from ..schemas import ProjectSchema

projects_schema = ProjectSchema(many=True, strict=True)


class ProjectIndexResource(Resource):
    def get(self):
        """
        Return a list of projects.
        """
        query = Project.query.options(
            joinedload('organization'),
            joinedload('repository'),
        ).all()
        return self.respond_with_schema(projects_schema, query)
