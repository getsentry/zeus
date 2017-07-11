from marshmallow import Schema
from flask import current_app, jsonify, request, Response
from flask.views import View
from time import sleep

from ..authentication import ApiTokenAuthentication


class AuthenticationFailed(Exception):
    pass


class Resource(View):
    methods = ['GET', 'POST', 'PUT', 'DELETE']

    authentication_classes = (ApiTokenAuthentication, )

    def dispatch_request(self, *args, **kwargs) -> Response:
        delay = current_app.config.get('API_DELAY', 0)
        if delay:
            sleep(delay / 1000)

        for auth_cls in self.authentication_classes:
            try:
                if auth_cls().authenticate():
                    break
            except AuthenticationFailed:
                return self.respond({'message': 'invalid credentials'}, 401)

        try:
            method = getattr(self, request.method.lower())
        except AttributeError:
            return self.respond({'message': 'resource not found'}, 405)

        resp = method(*args, **kwargs)
        if isinstance(resp, Response):
            return resp
        return self.respond(resp)

    def not_found(self, message: str='resource not found') -> Response:
        return self.error(message, 404)

    def error(self, message: str='resource not found', status: int=403) -> Response:
        return self.respond({'message': message}, status)

    def respond(self, context: dict={}, status: int=200) -> Response:
        resp = jsonify(context)
        resp.status_code = status
        return resp

    def schema_from_request(self, schema: Schema, partial=False):
        return schema.load(request.get_json() or {}, partial=partial)

    def respond_with_schema(self, schema: Schema, value, status: int=200) -> Response:
        result = schema.dump(value)
        if result.errors:
            return self.error('invalid schema supplied')
        return self.respond(result.data, status)
