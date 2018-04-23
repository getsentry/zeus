from json import dumps
from flask import current_app, Response
from functools import partialmethod
from typing import Mapping, BinaryIO

from zeus import auth
from zeus.exceptions import ApiError


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
        data: dict = None,
        files: Mapping[str, BinaryIO] = None,
        json: dict = None,
        params: dict = None,
        request=None,
        tenant=True,
    ) -> Response:
        if request:
            assert not json
            assert not data
            assert not files
            data = request.data
            files = request.files
            json = None
            params = request.args

        if tenant is True:
            tenant = auth.get_current_tenant()

        if json:
            assert not data
            data = dumps(json)
            content_type = "application/json"
        elif files:
            if not data:
                data = {}
            for key, value in request.form.items():
                data[key] = value
            for key, value in files.items():
                data[key] = value
            content_type = "multipart/form-data"
        else:
            content_type = None

        with current_app.test_client() as client:
            response = client.open(
                path="/api/{}".format(path.lstrip("/")),
                query_string=params,
                method=method,
                content_type=content_type,
                data=data,
                environ_overrides={"zeus.tenant": tenant},
            )
        if not (200 <= response.status_code < 300):
            raise ApiError(
                text=response.get_data(as_text=True), code=response.status_code
            )

        if response.headers["Content-Type"] != "application/json":
            raise ApiError(
                text="Request returned invalid content type: {}".format(
                    response.headers["Content-Type"]
                ),
                code=response.status_code,
            )

        return response

    delete = partialmethod(dispatch, method="DELETE")
    get = partialmethod(dispatch, method="GET")
    head = partialmethod(dispatch, method="HEAD")
    options = partialmethod(dispatch, method="OPTIONS")
    patch = partialmethod(dispatch, method="PATCH")
    post = partialmethod(dispatch, method="POST")
    put = partialmethod(dispatch, method="PUT")


api_client = APIClient()
delete = api_client.delete
get = api_client.get
head = api_client.head
options = api_client.options
patch = api_client.patch
post = api_client.post
put = api_client.put
