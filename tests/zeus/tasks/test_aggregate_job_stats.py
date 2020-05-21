from zeus import factories
from zeus.constants import Result, Status
from zeus.models import FailureReason, ItemStat
from zeus.tasks import (
    aggregate_build_stats,
    aggregate_build_stats_for_job,
    record_bundle_stats,
)


def test_unfinished_job(mocker, db_session, default_revision, default_tenant):
    build = factories.BuildFactory(revision=default_revision, queued=True)
    db_session.add(build)

    job = factories.JobFactory(build=build, in_progress=True)
    db_session.add(job)

    aggregate_build_stats(build.id)

    assert build.status == Status.in_progress
    assert build.result == Result.unknown


def test_finished_job(mocker, db_session, default_revision, default_tenant):
    build = factories.BuildFactory(revision=default_revision, in_progress=True)
    db_session.add(build)

    job = factories.JobFactory(build=build, failed=True)
    db_session.add(job)

    mock_delay = mocker.patch("zeus.config.celery.delay")

    aggregate_build_stats(build.id)

    assert build.status == Status.finished
    assert build.result == Result.failed

    mock_delay.assert_called_once_with(
        "zeus.send_build_notifications", build_id=build.id
    )


def test_no_jobs(mocker, db_session, default_revision, default_tenant):
    build = factories.BuildFactory(revision=default_revision, finished=True)
    db_session.add(build)

    aggregate_build_stats(build.id)

    db_session.refresh(build)

    assert build.result == Result.errored

    reasons = list(FailureReason.query.filter(FailureReason.build_id == build.id))
    assert len(reasons) == 1
    assert reasons[0].reason == FailureReason.Reason.no_jobs
    assert reasons[0].job_id is None


def test_failing_tests(mocker, db_session, default_revision, default_tenant):
    build = factories.BuildFactory(revision=default_revision, in_progress=True)
    db_session.add(build)

    job = factories.JobFactory(build=build, passed=True)
    db_session.add(job)

    factories.TestCaseFactory(job=job, failed=True)

    aggregate_build_stats_for_job(job.id)
    aggregate_build_stats(build.id)

    assert job.result == Result.failed
    assert build.result == Result.failed

    reasons = list(FailureReason.query.filter(FailureReason.job_id == job.id))
    assert len(reasons) == 1
    assert reasons[0].reason == FailureReason.Reason.failing_tests


def test_failing_tests_duplicate_reason(
    mocker, db_session, default_revision, default_tenant
):
    build = factories.BuildFactory(revision=default_revision, in_progress=True)
    db_session.add(build)

    job = factories.JobFactory(build=build, passed=True)
    db_session.add(job)

    factories.TestCaseFactory(job=job, failed=True)

    db_session.add(
        FailureReason(
            build_id=build.id,
            reason=FailureReason.Reason.failing_tests,
            job_id=job.id,
            repository_id=job.repository_id,
        )
    )

    aggregate_build_stats_for_job(job.id)

    assert job.result == Result.failed

    reasons = list(FailureReason.query.filter(FailureReason.job_id == job.id))
    assert len(reasons) == 1
    assert reasons[0].reason == FailureReason.Reason.failing_tests


def test_failure_with_allow_failure(
    mocker, db_session, default_revision, default_tenant
):
    build = factories.BuildFactory(revision=default_revision, in_progress=True)
    db_session.add(build)

    job = factories.JobFactory(build=build, failed=True, allow_failure=True)
    db_session.add(job)

    aggregate_build_stats(build.id)

    assert build.status == Status.finished
    assert build.result == Result.passed


def test_newly_unfinished_job(mocker, db_session, default_revision, default_tenant):
    build = factories.BuildFactory(revision=default_revision, finished=True)
    db_session.add(build)

    job = factories.JobFactory(build=build, in_progress=True)
    db_session.add(job)

    aggregate_build_stats(build.id)

    assert build.status == Status.in_progress
    assert build.result == Result.unknown


def test_coverage_stats(mocker, db_session, default_revision, default_tenant):
    build = factories.BuildFactory(revision=default_revision)
    db_session.add(build)

    job = factories.JobFactory(build=build, passed=True)
    db_session.add(job)

    db_session.add(
        factories.FileCoverageFactory(
            build=build,
            lines_covered=20,
            lines_uncovered=50,
            diff_lines_covered=5,
            diff_lines_uncovered=2,
        )
    )
    db_session.add(
        factories.FileCoverageFactory(
            build=build,
            lines_covered=10,
            lines_uncovered=10,
            diff_lines_covered=5,
            diff_lines_uncovered=0,
        )
    )

    aggregate_build_stats(build.id)

    stats = {
        i.name: i.value
        for i in ItemStat.query.filter(
            ItemStat.item_id == build.id,
            ItemStat.name.in_(
                [
                    "coverage.lines_covered",
                    "coverage.lines_uncovered",
                    "coverage.diff_lines_covered",
                    "coverage.diff_lines_uncovered",
                ]
            ),
        )
    }
    assert stats["coverage.lines_covered"] == 30
    assert stats["coverage.lines_uncovered"] == 60
    assert stats["coverage.diff_lines_covered"] == 10
    assert stats["coverage.diff_lines_uncovered"] == 2


def test_test_stats(mocker, db_session, default_revision, default_tenant):
    build = factories.BuildFactory(revision=default_revision, in_progress=True)
    db_session.add(build)

    job = factories.JobFactory(build=build, passed=True)
    db_session.add(job)
    job2 = factories.JobFactory(build=build, passed=True)
    db_session.add(job2)

    db_session.add(
        factories.TestCaseFactory(job=job, name="foo", failed=True, duration=8)
    )
    db_session.add(
        factories.TestCaseFactory(job=job, name="bar", passed=True, duration=2)
    )

    db_session.add(
        factories.TestCaseFactory(job=job2, name="bar", failed=True, duration=2)
    )

    aggregate_build_stats_for_job(job.id)
    aggregate_build_stats_for_job(job2.id)
    aggregate_build_stats(build.id)

    build_stats = {
        i.name: i.value for i in ItemStat.query.filter(ItemStat.item_id == build.id)
    }
    assert build_stats["tests.count"] == 3
    assert build_stats["tests.count_unique"] == 2
    assert build_stats["tests.failures"] == 2
    assert build_stats["tests.failures_unique"] == 2
    assert build_stats["tests.duration"] == 12

    job_stats = {
        i.name: i.value for i in ItemStat.query.filter(ItemStat.item_id == job.id)
    }
    assert job_stats["tests.count"] == 2
    assert job_stats["tests.failures"] == 1
    assert job_stats["tests.duration"] == 10


def test_record_bundle_stats(mocker, db_session, default_revision, default_tenant):
    build = factories.BuildFactory(revision=default_revision, in_progress=True)
    db_session.add(build)

    job = factories.JobFactory(build=build, passed=True)
    db_session.add(job)

    bundle = factories.BundleFactory(job=job)
    db_session.add(factories.BundleFactory(job=job))
    db_session.add(factories.BundleAssetFactory(bundle=bundle, size=1000))
    db_session.add(factories.BundleAssetFactory(bundle=bundle, size=1500))

    record_bundle_stats(job.id)

    job_stats = {
        i.name: i.value for i in ItemStat.query.filter(ItemStat.item_id == job.id)
    }
    assert job_stats["bundle.total_asset_size"] == 2500


def test_aggregate_build_stats_for_job_triggers_testcase_rollup(
    mocker, db_session, default_revision, default_tenant
):
    mock_delay = mocker.patch("zeus.config.celery.delay")

    build = factories.BuildFactory(revision=default_revision, passed=True)
    db_session.add(build)

    job = factories.JobFactory(build=build, passed=True)
    db_session.add(job)

    factories.TestCaseFactory(job=job, passed=True)

    aggregate_build_stats_for_job(job.id)

    mock_delay.assert_any_call("zeus.rollup_testcases_for_job", job_id=job.id)
