import zeus

from enum import Enum, IntEnum, IntFlag


class Status(IntEnum):
    unknown = 0
    queued = 1
    in_progress = 2
    finished = 3
    collecting_results = 4
    expired = 5  # used for artifacts

    def __str__(self):
        return self.name


class Result(IntEnum):
    unknown = 0
    aborted = 5
    passed = 1
    skipped = 3
    errored = 4
    failed = 2

    def __str__(self):
        return self.name


class Severity(IntEnum):
    unknown = 0
    ignore = 1
    info = 2
    warning = 3
    error = 4

    def __str__(self):
        return self.name


class Permission(IntFlag):
    none = 0
    read = 1
    write = 3
    admin = 7

    def __str__(self):
        return self.name


class DeactivationReason(Enum):
    invalid_pubkey = "invalid_pubkey"


STATUS_PRIORITY = (
    Status.in_progress,
    Status.queued,
    Status.collecting_results,
    Status.finished,
)

RESULT_PRIORITY = (
    Result.errored,
    Result.aborted,
    Result.failed,
    Result.unknown,
    Result.passed,
    Result.skipped,
)

PERMISSION_MAP = {
    "GET": Permission.read,
    "POST": Permission.write,
    "PUT": Permission.write,
    "DELETE": Permission.admin,
}


GITHUB_AUTH_URI = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URI = "https://github.com/login/oauth/access_token"
GITHUB_DEFAULT_SCOPES = ("user:email", "repo", "read:org")

USER_AGENT = "zeus/{0}".format(zeus.VERSION)

VCS_CLEANUP_INTERVAL = 3600 * 24  # 24 ours
