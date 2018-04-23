from zeus.config import db
from zeus.models import Hook

from .base_hook import BaseHookResource
from ..schemas import HookSchema

hook_schema = HookSchema(strict=True)


class HookDetailsResource(BaseHookResource):

    def get(self, hook: Hook):
        """
        Return a hook.
        """
        return self.respond_with_schema(hook_schema, hook)

    def put(self, hook: Hook):
        """
        Update a hook.
        """
        hook_schema = HookSchema(strict=True, context={"hook": hook})
        result = self.schema_from_request(hook_schema, partial=True)
        if result.errors:
            return self.respond(result.errors, 403)

        if db.session.is_modified(hook):
            db.session.add(hook)
            db.session.commit()
        return self.respond_with_schema(hook_schema, hook)

    def delete(self, hook: Hook):
        """
        Delete a hook.
        """
        db.session.delete(hook)
        db.session.commit()
        return self.respond(status=204)
