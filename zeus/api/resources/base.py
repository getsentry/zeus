from marshmallow import Schema
from flask import jsonify, request, Response
from flask.views import View


class Resource(View):
    methods = ['GET', 'POST', 'PUT', 'DELETE']

    def dispatch_request(self, *args, **kwargs) -> Response:
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

    def schema_from_request(self, schema: Schema):
        return schema.load(request.get_json() or {})

    def respond_with_schema(self, schema: Schema, value, status: int=200) -> Response:
        result = schema.dump(value)
        if result.errors:
            return self.error('invalid schema supplied')
        return self.respond(result.data, status)
