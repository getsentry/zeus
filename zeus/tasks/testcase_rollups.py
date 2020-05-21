
import sentry_sdk

from uuid import UUID

from zeus.config import celery, db
from zeus.constants import Result
from zeus.db.utils import create_or_update
from zeus.models import TestCase, TestCaseRollup


@celery.task(
    name="zeus.rollup_testcase",
    max_retries=5,
    autoretry_for=(Exception,),
    acks_late=True,
    time_limit=10,
)
def rollup_testcase(testcase_id: UUID):
    testcase = TestCase.query.unrestricted_unsafe().get(testcase_id)
    assert testcase

    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("repository_id", str(testcase.repository_id))
        scope.set_tag("job_id", str(testcase.job_id))

    create_or_update(
        model=TestCaseRollup,
        where={
            "repository_id": testcase.repository_id,
            "hash": testcase.hash,
            "date": testcase.job.date_finished.date(),
        },
        values={
            "name": testcase.name,
            "runs_failed": TestCaseRollup.runs_failed
            + (1 if testcase.result == Result.failed else 0),
            "runs_passed": TestCaseRollup.runs_passed
            + (1 if testcase.result == Result.passed else 0),
            "total_runs": TestCaseRollup.total_runs + 1,
            "total_duration": TestCaseRollup.total_duration + testcase.duration,
        },
        create_values={
            "name": testcase.name,
            "runs_failed": 1 if testcase.result == Result.failed else 0,
            "runs_passed": 1 if testcase.result == Result.passed else 0,
            "total_runs": 1,
            "total_duration": testcase.duration,
        },
    )


@celery.task(
    name="zeus.rollup_testcases_for_job",
    max_retries=5,
    autoretry_for=(Exception,),
    acks_late=True,
    time_limit=60,
)
def rollup_testcases_for_job(job_id: UUID):
    query = db.session.query(TestCase.id).filter(TestCase.job_id == job_id)
    for (testcase_id,) in query:
        celery.delay("zeus.rollup_testcase", testcase_id=testcase_id)
