import json

from collections import OrderedDict
from json.decoder import JSONDecodeError
from typing import Optional


class AuthenticationFailed(Exception):
    pass


class ApiError(Exception):
    code: Optional[int] = None
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
        super(ApiError, self).__init__(
            "code={} reason={}".format(self.code, (text or "")[:128])
        )

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

    def get_upgrade_url(self) -> Optional[str]:
        if self.identity.provider == "github":
            return "/auth/github"


class UnknownRepositoryBackend(Exception):
    pass


class UnknownBuild(Exception):
    pass


class UnknownJob(Exception):
    pass


class CommandError(Exception):
    def __init__(
        self,
        cmd: str = None,
        retcode: int = None,
        stdout: bytes = None,
        stderr: bytes = None,
    ):
        self.cmd = cmd
        self.retcode = retcode
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        if self.cmd:
            return "%s returned %d:\nSTDOUT: %r\nSTDERR: %r" % (
                self.cmd,
                self.retcode,
                self.stdout.decode("utf-8"),
                self.stderr.decode("utf-8"),
            )
        return ""


class UnknownRevision(CommandError):
    def __init__(self, ref=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ref = ref

    def __str__(self):
        if self.ref:
            return self.ref
        return super().__str__()


class InvalidPublicKey(CommandError):
    pass
