from flask import current_app, jsonify, request, Response
from flask.views import View
from sqlalchemy.orm import joinedload

from zeus import auth
from zeus.exceptions import APIError
from zeus.models import Hook


class BaseHook(View):
    methods = ['GET', 'POST', 'PUT', 'DELETE']

    def dispatch_request(self, hook_id, signature, *args, **kwargs) -> Response:
        current_app.logger.info('received webhook id=%s', hook_id)

        hook = Hook.query.unrestricted_unsafe().options(
            joinedload('repository'),
        ).get(hook_id)
        if not hook.is_valid_signature(signature):
            current_app.logger.warn('invalid webhook signature id=%s', hook_id)
            return '', 403

        try:
            method = getattr(self, request.method.lower())
        except AttributeError:
            current_app.logger.warn(
                'invalid webhook method id=%s, method=%s', hook_id, request.method)
            return self.respond({'message': 'resource not found'}, 405)

        auth.set_current_tenant(auth.Tenant(
            repository_ids=[hook.repository_id]))

        try:
            resp = method(hook, *args, **kwargs)
        except APIError as exc:
            return self.respond(exc.json, exc.code)
        if isinstance(resp, Response):
            return resp
        return self.respond(resp)

    def respond(self, context: dict={}, status: int=200) -> Response:
        resp = jsonify(context)
        resp.status_code = status
        return resp
