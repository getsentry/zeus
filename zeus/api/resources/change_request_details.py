from zeus.config import db
from zeus.models import ChangeRequest

from .base_change_request import BaseChangeRequestResource
from ..schemas import ChangeRequestSchema


class ChangeRequestDetailsResource(BaseChangeRequestResource):
    def select_resource_for_update(self):
        return False

    def get(self, cr: ChangeRequest):
        schema = ChangeRequestSchema()
        return self.respond_with_schema(schema, cr)

    def put(self, cr: ChangeRequest):
        schema = ChangeRequestSchema(
            context={"repository": cr.repository, "change_request": cr}
        )
        self.schema_from_request(schema, partial=True)
        if db.session.is_modified(cr):
            db.session.add(cr)
            db.session.commit()
        return self.respond_with_schema(schema, cr)
