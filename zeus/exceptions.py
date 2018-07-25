import json

from collections import OrderedDict
from json.decoder import JSONDecodeError


class AuthenticationFailed(Exception):
    pass


class ApiError(Exception):
    code = None
    json = None

    def __init__(self, text=None, code=None):
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
        super(ApiError, self).__init__((text or "")[:128])

    @classmethod
    def from_response(cls, response):
        if response.status_code == 401:
            return ApiUnauthorized(response.text)

        return cls(response.text, response.status_code)


class ApiUnauthorized(ApiError):
    code = 401


class IdentityNeedsUpgrade(ApiUnauthorized):
    def __init__(self, scope, identity):
        ApiUnauthorized.__init__(self)
        self.scope = scope
        self.identity = identity

    def get_upgrade_url(self):
        if self.identity.provider == "github":
            return "/auth/github"


class MissingRevision(Exception):
    def __init__(self, msg=None, sha=None, *args):
        Exception.__init__(self, msg)
        self.sha = sha
