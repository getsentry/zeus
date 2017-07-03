from enum import Enum


class Status(Enum):
    unknown = 0
    queued = 1
    in_progress = 2
    finished = 3

    def __str__(self):
        return STATUS_LABELS[self]


class Result(Enum):
    unknown = 0
    aborted = 5
    passed = 1
    skipped = 3
    failed = 2

    def __str__(self):
        return RESULT_LABELS[self]


STATUS_LABELS = {
    Status.unknown: 'Unknown',
    Status.queued: 'Queued',
    Status.in_progress: 'In progress',
    Status.finished: 'Finished',
}

STATUS_PRIORITY = (
    Status.in_progress,
    Status.queued,
    Status.finished,
)

RESULT_LABELS = {
    Result.unknown: 'Unknown',
    Result.passed: 'Passed',
    Result.failed: 'Failed',
    Result.skipped: 'Skipped',
    Result.aborted: 'Aborted',
}

RESULT_PRIORITY = (
    Result.aborted,
    Result.failed,
    Result.unknown,
    Result.passed,
    Result.skipped,
)
