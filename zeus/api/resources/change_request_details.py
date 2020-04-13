from zeus.config import celery, db
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

        if not cr.parent_revision_sha or (not cr.head_revision_sha and cr.head_ref):
            celery.delay("zeus.resolve_ref_for_change_request", change_request_id=cr.id)

        return self.respond_with_schema(schema, cr)
