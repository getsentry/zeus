from flask import Response

from zeus.models import Organization

from .base import Resource


class BaseOrganizationResource(Resource):
    def dispatch_request(self, org_name: str, *args, **kwargs) -> Response:
        org = Organization.query.filter(
            Organization.name == org_name,
        ).first()
        if not org:
            return self.not_found()
        return Resource.dispatch_request(self, org, *args, **kwargs)
