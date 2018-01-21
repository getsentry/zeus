from marshmallow import Schema
from flask import current_app, jsonify, request, Response
from flask.views import View
from time import sleep
from urllib.parse import quote

from zeus import auth
from zeus.exceptions import ApiUnauthorized

from ..authentication import ApiTokenAuthentication, SessionAuthentication

LINK_HEADER = '<{uri}&page={page}>; rel="{name}" page="{page}"'


class Resource(View):
    methods = ['GET', 'POST', 'PUT', 'DELETE']

    authentication_classes = (ApiTokenAuthentication, SessionAuthentication)

    auth_required = True

    permission_overrides = {}

    def is_mutation(self) -> bool:
        return request.method in ('DELETE', 'PATCH', 'POST', 'PUT')

    def select_resurce_for_update(self) -> bool:
        # should the base resource treat it's query operations as locking
        # and utilize SELECT_FOR_UPDATE?
        # return self.is_mutation()
        return False

    def dispatch_request(self, *args, **kwargs) -> Response:
        delay = current_app.config.get('API_DELAY', 0)
        if delay:
            sleep(delay / 1000)

        tenant = request.environ.get('zeus.tenant')
        if self.authentication_classes:
            for auth_cls in self.authentication_classes:
                try:
                    _tenant = auth_cls().authenticate()
                    if _tenant:
                        tenant = _tenant
                        break
                except auth.AuthenticationFailed:
                    return self.respond({
                        'error': 'invalid_auth',
                    }, 401)

        if tenant:
            auth.set_current_tenant(tenant)
        elif self.auth_required:
            return self.respond({
                'error': 'auth_required',
            }, 401)

        try:
            method = getattr(self, request.method.lower())
        except AttributeError:
            return self.respond({'message': 'resource not found'}, 405)

        try:
            resp = method(*args, **kwargs)
            if not isinstance(resp, Response):
                resp = self.respond(resp)
            if tenant:
                resp.headers['X-Stream-Token'] = auth.generate_token(tenant)
            return resp
        except ApiUnauthorized:
            return self.respond({
                'error': 'auth_required',
            }, 401)
        except Exception:
            current_app.logger.exception('failed to handle api request')
            return self.error('internal server error', 500)

    def not_found(self, message: str='resource not found') -> Response:
        return self.error(message, 404)

    def error(self, message: str='resource not found', status: int=403) -> Response:
        return self.respond({'message': message}, status)

    def respond(self, context: dict={}, status: int=200) -> Response:
        resp = jsonify(context)
        resp.status_code = status
        return resp

    def schema_from_request(self, schema: Schema, partial=False):
        return schema.load(request.get_json() or request.form, partial=partial)

    def respond_with_schema(self, schema: Schema, value, status: int=200) -> Response:
        result = schema.dump(value)
        if result.errors:
            return self.error('invalid schema supplied')
        return self.respond(result.data, status)

    def paginate_with_schema(self, schema: Schema, query,
                             default_per_page: int=100, max_per_page: int=None) -> Response:
        page = int(request.args.get('page', 1))
        if not (page > 0):
            page = 1

        if max_per_page is None:
            max_per_page = default_per_page

        per_page = int(request.args.get('per_page', default_per_page))
        if per_page > max_per_page:
            per_page = max_per_page

        querystring = u'&'.join(
            u'{0}={1}'.format(quote(k), quote(v))
            for k, v in request.args.items()
            if k != 'page'
        )
        base_url = request.url.split('?', 1)[0]
        if querystring:
            base_url = '{0}?{1}'.format(base_url, querystring)
        else:
            base_url = base_url + '?'

        links = [LINK_HEADER.format(
            uri=base_url,
            name='next',
            page=page + 1,
        )]
        if page > 1:
            links.append(LINK_HEADER.format(
                uri=base_url,
                name='previous',
                page=page - 1,
            ))

        result = query.offset((page - 1) * per_page).limit(per_page)

        response = self.respond_with_schema(schema, result)
        response.headers['X-Hits'] = query.count()
        response.headers['Link'] = ', '.join(links)
        return response
