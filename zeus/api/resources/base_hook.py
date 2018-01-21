from flask import request, Response

from zeus import auth
from zeus.constants import Permission, PERMISSION_MAP
from zeus.models import Hook

from .base import Resource


class BaseHookResource(Resource):
    permission_overrides = {
        'DELETE': Permission.admin,
        'GET': Permission.admin,
        'PUT': Permission.admin,
        'POST': Permission.admin,
    }

    def dispatch_request(self, hook_id: str, *args, **kwargs) -> Response:
        queryset = Hook.query.filter(
            Hook.id == hook_id,
        )
        if self.select_resurce_for_update():
            queryset = queryset.with_for_update()
        hook = queryset.first()
        if not hook:
            return self.not_found()
        tenant = auth.get_current_tenant()
        required_permission = self.permission_overrides.get(
            request.method, PERMISSION_MAP[request.method]
        )
        if not tenant.has_permission(hook.repository_id, required_permission):
            return self.error('permission denied', 400)
        return Resource.dispatch_request(self, hook, *args, **kwargs)
