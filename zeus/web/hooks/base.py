from flask import current_app, jsonify, request, Response
from flask.views import View
from sqlalchemy.orm import joinedload

from zeus import auth
from zeus.config import nplusone
from zeus.constants import Permission
from zeus.exceptions import ApiError
from zeus.models import Hook


class BaseHook(View):
    public = False

    methods = ["GET", "POST", "PUT", "DELETE"]

    def dispatch_request(self, hook_id, signature=None, *args, **kwargs) -> Response:
        current_app.logger.info("received webhook id=%s", hook_id)

        with nplusone.ignore("eager_load"):
            hook = (
                Hook.query.unrestricted_unsafe()
                .options(joinedload("repository"))
                .get(hook_id)
            )

        if not hook:
            return self.respond({"message": "hook not found"}, 404)

        if not self.public and not hook.is_valid_signature(signature):
            current_app.logger.warn("invalid webhook signature id=%s", hook_id)
            return "", 403

        try:
            method = getattr(self, request.method.lower())
        except AttributeError:
            current_app.logger.warn(
                "invalid webhook method id=%s, method=%s", hook_id, request.method
            )
            return self.respond({"message": "resource not found"}, 405)

        auth.set_current_tenant(
            auth.RepositoryTenant(
                repository_id=hook.repository_id, permission=Permission.admin
            )
        )

        try:
            resp = method(hook, *args, **kwargs)
        except ApiError as exc:
            return self.respond(exc.json, exc.code)

        if isinstance(resp, Response):
            return resp

        return self.respond(resp)

    def respond(self, context: dict = {}, status: int = 200) -> Response:
        resp = jsonify(context)
        resp.status_code = status
        return resp
