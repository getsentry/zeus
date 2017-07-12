from json import dumps
from flask import current_app, Response
from flask.testing import make_test_environ_builder
from typing import Mapping, BinaryIO
from werkzeug.test import Client


class APIError(Exception):
    pass


class APIClient(object):
    """
    An internal API client.

    >>> client = APIClient()
    >>> response = client.get('/projects/')
    >>> print response
    """

    def dispatch(
        self,
        path: str,
        method: str,
        data: dict=None,
        files: Mapping[str, BinaryIO]=None,
        json: dict=None,
        request=None
    ) -> Response:
        if request:
            assert not json
            assert not data
            assert not files
            data = request.data
            files = request.files
            json = None

        if json:
            assert not data
            data = dumps(json)

        builder = make_test_environ_builder(
            app=current_app,
            path='/api/{}'.format(path.lstrip('/')),
            method=method,
            content_type=request.content_type if request else 'application/json',
            data=data,
        )
        if files:
            for key, value in files.items():
                builder.files[key] = value

        with current_app.test_client() as client:
            # XXX(dcramer): FlaskClient does not accept the builder argument
            response = Client.open(client, builder)
        if not (200 <= response.status_code < 300):
            raise APIError('Request returned invalid status code: %d' % (response.status_code, ))
        if response.headers['Content-Type'] != 'application/json':
            raise APIError(
                'Request returned invalid content type: %s' % (response.headers['Content-Type'], )
            )
        # TODO(dcramer): ideally we wouldn't encode + decode this
        return response

    def delete(self, *args, **kwargs):
        return self.dispatch(method='DELETE', *args, **kwargs)

    def get(self, *args, **kwargs):
        return self.dispatch(method='GET', *args, **kwargs)

    def head(self, *args, **kwargs):
        return self.dispatch(method='HEAD', *args, **kwargs)

    def options(self, *args, **kwargs):
        return self.dispatch(method='OPTIONS', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.dispatch(method='PATCH', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.dispatch(method='POST', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.dispatch(method='PUT', *args, **kwargs)


api_client = APIClient()
delete = api_client.delete
get = api_client.get
head = api_client.head
options = api_client.options
patch = api_client.patch
post = api_client.post
put = api_client.put
