from zeus.config import db
from zeus.models import ChangeRequest

from .base_change_request import BaseChangeRequestResource
from ..schemas import ChangeRequestSchema


class ChangeRequestDetailsResource(BaseChangeRequestResource):
    def select_resurce_for_update(self):
        return True

    def get(self, cr: ChangeRequest):
        schema = ChangeRequestSchema(strict=True)
        return self.respond_with_schema(schema, cr)

    def put(self, cr: ChangeRequest):
        schema = ChangeRequestSchema(
            context={'repository': cr.repository, 'change_request': cr})
        result = self.schema_from_request(schema, partial=True)
        if result.errors:
            return self.respond(result.errors, 403)
        if db.session.is_modified(cr):
            db.session.add(cr)
            db.session.commit()
        return self.respond_with_schema(schema, cr)
