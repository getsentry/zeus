from zeus import auth
from zeus.models import Organization

from .base import Resource
from ..schemas import OrganizationSchema

organization_schema = OrganizationSchema(strict=True)
organizations_schema = OrganizationSchema(many=True, strict=True)


class OrganizationIndexResource(Resource):
    def get(self):
        """
        Return a list of organizations.
        """
        query = Organization.query.all()
        return self.respond_with_schema(organizations_schema, query)

    def post(self, org: Organization):
        # TODO(dcramer): for now we're aiming for ease-of-use GH setup
        # so we'll unlock custom orgs down the road
        raise NotImplementedError

        result = self.schema_from_request(organization_schema)
        if result.errors:
            return self.respond(result.errors, 403)
        data = result.data
        org = Organization(**data)
        db.session.add(project)
        db.session.add(
            OrganizationAccess(
                user_id=auth.get_current_user().id,
                organization_id=org.id,
            )
        )
        db.session.commit()

        return self.respond_with_schema(organization_schema, project)
