from flask import jsonify, request
from flask.views import View


class Resource(View):
    methods = ['GET', 'POST', 'PUT', 'DELETE']

    def dispatch_request(self, *args, **kwargs):
        try:
            method = getattr(self, request.method.lower())
        except AttributeError:
            resp = jsonify({'message': 'resource not found'})
            resp.status_code == 405
            return resp
        resp = method(*args, **kwargs)
        return jsonify(resp)
