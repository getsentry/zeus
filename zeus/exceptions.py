import json

from collections import OrderedDict
from json.decoder import JSONDecodeError


class ApiError(Exception):
    code = None
    json = None
    xml = None

    def __init__(self, text, code=None):
        if code is not None:
            self.code = code
        self.text = text
        if text:
            try:
                self.json = json.loads(text, object_pairs_hook=OrderedDict)
            except (JSONDecodeError, ValueError):
                self.json = None
        else:
            self.json = None
        super(ApiError, self).__init__(text[:128])

    @classmethod
    def from_response(cls, response):
        if response.status_code == 401:
            return ApiUnauthorized(response.text)
        return cls(response.text, response.status_code)


class ApiUnauthorized(ApiError):
    code = 401
