import zeus

from enum import Enum


class Status(Enum):
    unknown = 0
    queued = 1
    in_progress = 2
    finished = 3
    collecting_results = 4

    def __str__(self):
        return self.name


class Result(Enum):
    unknown = 0
    aborted = 5
    passed = 1
    skipped = 3
    failed = 2

    def __str__(self):
        return self.name


STATUS_PRIORITY = (
    Status.in_progress,
    Status.queued,
    Status.collecting_results,
    Status.finished,
)

RESULT_PRIORITY = (
    Result.aborted,
    Result.failed,
    Result.unknown,
    Result.passed,
    Result.skipped,
)

GITHUB_AUTH_URI = 'https://github.com/login/oauth/authorize'
GITHUB_TOKEN_URI = 'https://github.com/login/oauth/access_token'

USER_AGENT = 'zeus/{0}'.format(
    zeus.VERSION,
)
