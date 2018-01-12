from zeus.config import db
from zeus.models import Hook

from .base import Resource
from ..schemas import HookSchema

hook_schema = HookSchema(strict=True)

UNSET = object()


class HookDetailsResource(Resource):
    def get(self, hook_id: str):
        """
        Return a hook.
        """
        hook = Hook.query.filter(
            Hook.id == hook_id,
        ).first()
        if not hook:
            return self.not_found()
        return self.respond_with_schema(hook_schema, hook)

    def put(self, hook_id: str):
        """
        Update a hook.
        """
        hook = Hook.query.filter(
            Hook.id == hook_id,
        ).first()
        if not hook:
            return self.not_found()
        hook_schema = HookSchema(strict=True, context={'hook': hook})
        result = self.schema_from_request(
            hook_schema, partial=True)
        if result.errors:
            return self.respond(result.errors, 403)
        if db.session.is_modified(hook):
            db.session.add(hook)
            db.session.commit()
        return self.respond_with_schema(hook_schema, hook)

    def delete(self, hook_id: str):
        """
        Delete a hook.
        """
        hook = Hook.query.filter(
            Hook.id == hook_id,
        ).first()
        if not hook:
            return self.not_found()
        db.session.delete(hook)
        db.session.commit()
        return self.respond(status=204)
