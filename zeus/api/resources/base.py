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

    def not_found(self, message: str = 'resource not found') -> Response:
        return self.error(message, 404)

    def error(self, message: str = 'resource not found', status: int = 403) -> Response:
        return self.respond({'message': message}, status)

    def respond(self, context={}, status: int = 200) -> Response:
        resp = jsonify(context)
        resp.status_code = status
        return resp
