from flask import jsonify, request, Response
from flask.views import View
from sqlalchemy.orm import joinedload

from zeus import auth
from zeus.models import Hook


class BaseHook(View):
    methods = ['GET', 'POST', 'PUT', 'DELETE']

    def dispatch_request(self, hook_id, signature, *args, **kwargs) -> Response:

        hook = Hook.query.unrestricted_unsafe().options(
            joinedload('project'),
            joinedload('organization'),
        ).get(hook_id)
        if not hook.is_valid_signature(signature):
            return '', 403

        try:
            method = getattr(self, request.method.lower())
        except AttributeError:
            return self.respond({'message': 'resource not found'}, 405)

        auth.set_current_tenant(
            auth.Tenant(
                organization_ids=[hook.project.organization_id],
                repository_ids=[hook.project.repository_id],
                project_ids=[hook.project_id],
            )
        )

        resp = method(hook, *args, **kwargs)
        if isinstance(resp, Response):
            return resp
        return self.respond(resp)

    def respond(self, context: dict={}, status: int=200) -> Response:
        resp = jsonify(context)
        resp.status_code = status
        return resp
