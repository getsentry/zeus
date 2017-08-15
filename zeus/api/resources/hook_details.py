from zeus.config import db
from zeus.models import Hook

from .base import Resource
from ..schemas import HookSchema

hook_schema = HookSchema(strict=True)


class HookDetailsResource(Resource):
    def get(self, hook_id: str):
        """
        Return a hook.
        """
        hook = Hook.query.filter(
            Hook.id == hook_id,
        ).first()
        return self.respond_with_schema(hook_schema, hook)

    def delete(self, hook_id: str):
        """
        Delete a hook.
        """
        hook = Hook.query.filter(
            Hook.id == hook_id,
        ).first()
        db.session.delete(hook)
        db.session.commit()
        return self.respond(status=204)
