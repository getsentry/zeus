# https://gist.github.com/pgjones/763b6aa223433d06583f
import json

from flask.testing import FlaskClient
from flask.wrappers import Response


class JSONResponseWrapper(Response):
    """
    Extends the BaseResponse to add a json method.
    """

    def json(self):
        """Return the json decoded content."""
        return json.loads(self.get_data(as_text=True))


class ZeusTestClient(FlaskClient):
    """
    Extends the FlaskClient request methods by adding json support.
    This should be used like so:

    >>> app.test_client_class = ZeusTestClient
    >>> client = app.test_client()
    >>> client.post(url, json=data)

    Note that this class will override any response_wrapper you wish to use.
    """

    def __init__(self, *args, **kwargs):
        """
        This ensures the response_wrapper is JSONResponseWrapper.
        """
        super(ZeusTestClient, self).__init__(
            args[0], response_wrapper=JSONResponseWrapper, **kwargs
        )

    def open(self, *args, **kwargs):
        json_data = kwargs.pop('json', None)
        if json_data is not None:
            if 'data' in kwargs:
                raise ValueError('Use either `json` or `data`, not both.')

            if 'content_type' not in kwargs:
                kwargs['content_type'] = 'application/json'
            kwargs['data'] = json.dumps(json_data)
        return super(ZeusTestClient, self).open(*args, **kwargs)
