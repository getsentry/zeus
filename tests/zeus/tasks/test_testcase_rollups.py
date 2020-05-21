from zeus import factories
from zeus.models import TestCaseRollup
from zeus.tasks import rollup_testcase, rollup_testcases_for_job


def test_rollup_testcases_for_job(mocker, db_session, default_revision, default_tenant):
    mock_delay = mocker.patch("zeus.config.celery.delay")

    build = factories.BuildFactory(revision=default_revision, passed=True)
    db_session.add(build)

    job = factories.JobFactory(build=build, passed=True)
    db_session.add(job)

    testcase = factories.TestCaseFactory(job=job, passed=True)

    rollup_testcases_for_job(job_id=job.id)

    mock_delay.assert_any_call("zeus.rollup_testcase", testcase_id=testcase.id)


def test_rollup_testcase(mocker, db_session, default_revision, default_tenant):
    build = factories.BuildFactory(revision=default_revision, passed=True)
    db_session.add(build)

    job = factories.JobFactory(build=build, passed=True)
    db_session.add(job)

    testcase = factories.TestCaseFactory(job=job, passed=True)
    factories.TestCaseFactory(job=job, passed=True)

    rollup_testcase(testcase_id=testcase.id)

    rollups = list(TestCaseRollup.query.unrestricted_unsafe().all())
    assert len(rollups) == 1

    rollup = rollups[0]
    assert rollup.repository_id == testcase.repository_id
    assert rollup.hash == testcase.hash
    assert rollup.name == testcase.name
    assert rollup.date == job.date_finished.date()
    assert rollup.runs_passed == 1
    assert rollup.runs_failed == 0
    assert rollup.total_runs == 1
    assert rollup.total_duration == testcase.duration

    job2 = factories.JobFactory(
        build=build, passed=True, date_finished=job.date_finished
    )
    testcase2 = factories.TestCaseFactory(job=job2, failed=True, name=testcase.name)

    rollup_testcase(testcase_id=testcase2.id)

    rollups = list(TestCaseRollup.query.unrestricted_unsafe().all())
    assert len(rollups) == 1

    rollup = rollups[0]
    assert rollup.repository_id == testcase.repository_id
    assert rollup.hash == testcase.hash
    assert rollup.name == testcase.name
    assert rollup.date == job.date_finished.date()
    assert rollup.runs_passed == 1
    assert rollup.runs_failed == 1
    assert rollup.total_runs == 2
    assert rollup.total_duration == testcase.duration + testcase2.duration
