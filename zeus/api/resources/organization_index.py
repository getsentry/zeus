from zeus.models import Organization

from .base import Resource
from ..schemas import OrganizationSchema

organizations_schema = OrganizationSchema(many=True, strict=True)


class OrganizationIndexResource(Resource):
    def get(self):
        """
        Return a list of organizations.
        """
        query = Organization.query.all()
        return self.respond_with_schema(organizations_schema, query)
