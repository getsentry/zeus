from json import dumps
from flask import current_app, Response
from functools import partialmethod
from typing import Mapping, BinaryIO


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
        elif files:
            if not data:
                data = {}
            for key, value in files.items():
                data[key] = value

        with current_app.test_client() as client:
            response = client.open(
                path='/api/{}'.format(path.lstrip('/')),
                method=method,
                content_type=(
                    request.content_type if request else ('application/json' if json else None)
                ),
                data=data,
            )
        if not (200 <= response.status_code < 300):
            raise APIError('Request returned invalid status code: %d' % (response.status_code, ))
        if response.headers['Content-Type'] != 'application/json':
            raise APIError(
                'Request returned invalid content type: %s' % (response.headers['Content-Type'], )
            )
        # TODO(dcramer): ideally we wouldn't encode + decode this
        return response

    delete = partialmethod(dispatch, method='DELETE')
    get = partialmethod(dispatch, method='GET')
    head = partialmethod(dispatch, method='HEAD')
    options = partialmethod(dispatch, method='OPTIONS')
    patch = partialmethod(dispatch, method='PATCH')
    post = partialmethod(dispatch, method='POST')
    put = partialmethod(dispatch, method='PUT')


api_client = APIClient()
delete = api_client.delete
get = api_client.get
head = api_client.head
options = api_client.options
patch = api_client.patch
post = api_client.post
put = api_client.put
