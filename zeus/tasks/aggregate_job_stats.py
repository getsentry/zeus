
import sentry_sdk

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from uuid import UUID

from zeus import auth
from zeus.config import celery, db, redis
from zeus.constants import Result, Status
from zeus.db.utils import create_or_update
from zeus.models import (
    Build,
    FailureReason,
    FileCoverage,
    ItemStat,
    Job,
    PendingArtifact,
    StyleViolation,
    TestCase,
    BundleAsset,
)
from zeus.utils import timezone
from zeus.utils.aggregation import aggregate_result, aggregate_status, safe_agg
from zeus.utils.artifacts import has_unprocessed_artifacts
from zeus.utils.sentry import span

AGGREGATED_BUILD_STATS = (
    "tests.count",
    "tests.duration",
    "tests.failures",
    "tests.count_unique",
    "tests.failures_unique",
    "style_violations.count",
    "bundle.total_asset_size",
)


# TODO(dcramer): put a lock around this


@celery.task(
    name="zeus.aggregate_build_stats_for_job",
    max_retries=5,
    autoretry_for=(Exception,),
    acks_late=True,
    time_limit=60,
)
def aggregate_build_stats_for_job(job_id: UUID):
    """
    Given a job, aggregate its data upwards into the Build.abs

    This should generally be fired upon a job's completion, or
    alternatively it can be used to repair aggregate data.
    """
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("job_id", str(job_id))

    lock_key = "job:{job_id}".format(job_id=job_id)
    with redis.lock(lock_key):
        job = (
            Job.query.unrestricted_unsafe()
            .with_for_update(nowait=True)
            .filter(Job.id == job_id)
            .first()
        )
        if not job:
            raise ValueError

        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("build_id", str(job.build_id))
            scope.set_tag("repository_id", str(job.repository_id))

        auth.set_current_tenant(auth.RepositoryTenant(repository_id=job.repository_id))

        # we need to handle the race between when the mutations were made to <Job> and
        # when the only remaining artifact may have finished processing
        if job.status == Status.collecting_results:
            if not has_unprocessed_artifacts(job):
                job.status = Status.finished
                if not job.date_finished:
                    job.date_finished = timezone.now()
                db.session.add(job)
                db.session.commit()
            else:
                pending_artifact_ids = db.session.query(PendingArtifact.id).filter(
                    PendingArtifact.repository_id == job.repository_id,
                    PendingArtifact.provider == job.provider,
                    PendingArtifact.external_build_id == job.build.external_id,
                    PendingArtifact.external_job_id == job.external_id,
                )
                for pa_id in pending_artifact_ids:
                    celery.delay(
                        "zeus.process_pending_artifact", pending_artifact_id=pa_id
                    )

        # record any job-specific stats that might not have been taken care elsewhere
        if job.status == Status.finished:
            if not job.date_finished:
                job.date_finished = timezone.now()
                db.session.add(job)
            record_test_stats(job.id)
            record_style_violation_stats(job.id)
            record_bundle_stats(job.id)
            record_failure_reasons(job)
            celery.delay("zeus.rollup_testcases_for_job", job_id=job.id)
            db.session.commit()

    lock_key = "aggstatsbuild:{build_id}".format(build_id=job.build_id.hex)
    with redis.lock(lock_key):
        celery.delay("zeus.aggregate_build_stats", build_id=job.build_id)


def aggregate_stat_for_build(build: Build, name: str, func_=func.sum):
    """
    Aggregates a single stat for all jobs the given build.
    """
    if name == "tests.count_unique":
        value = (
            db.session.query(func.count(TestCase.hash.distinct()))
            .join(Job, TestCase.job_id == Job.id)
            .filter(Job.build_id == build.id)
            .as_scalar()
        )
    elif name == "tests.failures_unique":
        value = (
            db.session.query(func.count(TestCase.hash.distinct()))
            .join(Job, TestCase.job_id == Job.id)
            .filter(TestCase.result == Result.failed, Job.build_id == build.id)
            .as_scalar()
        )
    else:
        value = (
            db.session.query(func.coalesce(func_(ItemStat.value), 0))
            .filter(
                ItemStat.item_id.in_(
                    db.session.query(Job.id).filter(Job.build_id == build.id)
                ),
                ItemStat.name == name,
            )
            .as_scalar()
        )

    create_or_update(
        model=ItemStat,
        where={"item_id": build.id, "name": name},
        values={"value": value},
    )


@span("record_failure_reasons")
def record_failure_reasons(job: Job):
    has_failures = db.session.query(
        TestCase.query.filter(
            TestCase.job_id == job.id, TestCase.result == Result.failed
        ).exists()
    ).scalar()
    any_failures = False

    if has_failures:
        any_failures = True
        try:
            with db.session.begin_nested():
                db.session.add(
                    FailureReason(
                        build_id=job.build_id,
                        job_id=job.id,
                        repository_id=job.repository_id,
                        reason=FailureReason.Reason.failing_tests,
                    )
                )
        except IntegrityError as exc:
            if "duplicate" not in str(exc):
                raise

    if any_failures and job.result == Result.passed:
        job.result = Result.failed
        db.session.add(job)

    db.session.flush()


@span("record_test_stats")
def record_test_stats(job_id: UUID):
    create_or_update(
        ItemStat,
        where={"item_id": job_id, "name": "tests.count"},
        values={
            "value": db.session.query(func.count(TestCase.id))
            .filter(TestCase.job_id == job_id)
            .as_scalar()
        },
    )
    create_or_update(
        ItemStat,
        where={"item_id": job_id, "name": "tests.failures"},
        values={
            "value": db.session.query(func.count(TestCase.id))
            .filter(TestCase.job_id == job_id, TestCase.result == Result.failed)
            .as_scalar()
        },
    )
    create_or_update(
        ItemStat,
        where={"item_id": job_id, "name": "tests.duration"},
        values={
            "value": db.session.query(func.coalesce(func.sum(TestCase.duration), 0))
            .filter(TestCase.job_id == job_id)
            .as_scalar()
        },
    )
    db.session.flush()


@span("record_coverage_stats")
def record_coverage_stats(build_id: UUID):
    """
    Aggregates all FileCoverage stats for the given build.
    """
    coverage_stats = (
        db.session.query(
            func.sum(FileCoverage.lines_covered).label("coverage.lines_covered"),
            func.sum(FileCoverage.lines_uncovered).label("coverage.lines_uncovered"),
            func.sum(FileCoverage.diff_lines_covered).label(
                "coverage.diff_lines_covered"
            ),
            func.sum(FileCoverage.diff_lines_uncovered).label(
                "coverage.diff_lines_uncovered"
            ),
        )
        .filter(FileCoverage.build_id == build_id)
        .group_by(FileCoverage.build_id)
        .first()
    )

    # TODO(dcramer): it'd be safer if we did this query within SQL
    stat_list = (
        "coverage.lines_covered",
        "coverage.lines_uncovered",
        "coverage.diff_lines_covered",
        "coverage.diff_lines_uncovered",
    )
    if not any(getattr(coverage_stats, n, None) is not None for n in stat_list):
        ItemStat.query.filter(
            ItemStat.item_id == build_id, ItemStat.name.in_(stat_list)
        ).delete(synchronize_session=False)
    else:
        for name in stat_list:
            create_or_update(
                model=ItemStat,
                where={"item_id": build_id, "name": name},
                values={"value": getattr(coverage_stats, name, 0) or 0},
            )


@span("record_style_violation_stats")
def record_style_violation_stats(job_id: UUID):
    create_or_update(
        ItemStat,
        where={"item_id": job_id, "name": "style_violations.count"},
        values={
            "value": db.session.query(func.coalesce(func.count(StyleViolation.id), 0))
            .filter(StyleViolation.job_id == job_id)
            .as_scalar()
        },
    )
    db.session.flush()


@span("record_bundle_stats")
def record_bundle_stats(job_id: UUID):
    create_or_update(
        ItemStat,
        where={"item_id": job_id, "name": "bundle.total_asset_size"},
        values={
            "value": db.session.query(func.coalesce(func.sum(BundleAsset.size), 0))
            .filter(BundleAsset.job_id == job_id)
            .as_scalar()
        },
    )
    db.session.flush()


@celery.task(
    name="zeus.aggregate_build_stats",
    max_retries=None,
    autoretry_for=(Exception,),
    acks_late=True,
    time_limit=60,
)
def aggregate_build_stats(build_id: UUID):
    """
    Updates various denormalized / aggregate attributes on Build per its
    jobs. These attributes include start and completion dates, as well as
    the status and result.
    """
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("build_id", str(build_id))

    # now we pull in the entirety of the build's data to aggregate state upward
    lock_key = "build:{build_id}".format(build_id=build_id)
    with redis.lock(lock_key, expire=60, nowait=True):
        build = (
            Build.query.unrestricted_unsafe().with_for_update(nowait=True).get(build_id)
        )
        if not build:
            raise ValueError("Unable to find build with id = {}".format(build_id))

        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("repository_id", str(build.repository_id))

        auth.set_current_tenant(
            auth.RepositoryTenant(repository_id=build.repository_id)
        )

        record_coverage_stats(build.id)

        job_list = list(Job.query.filter(Job.build_id == build.id))

        was_finished = build.status == Status.finished
        is_finished = all(p.status == Status.finished for p in job_list)

        # ensure build's dates are reflective of jobs
        build.date_started = safe_agg(
            min, (j.date_started for j in job_list if j.date_started)
        )

        if is_finished:
            build.date_finished = (
                safe_agg(max, (j.date_finished for j in job_list if j.date_finished))
            ) or timezone.now()
        else:
            build.date_finished = None

        pending_artifact_ids = list(
            db.session.query(PendingArtifact.id).filter(
                PendingArtifact.repository_id == build.repository_id,
                PendingArtifact.provider == build.provider,
                PendingArtifact.external_build_id == build.external_id,
            )
        )
        if pending_artifact_ids and is_finished:
            is_finished = False
            for pa_id in pending_artifact_ids:
                celery.call("zeus.process_pending_artifact", pending_artifact_id=pa_id)

        # if theres any failure, the build failed
        if any(j.result is Result.failed for j in job_list if not j.allow_failure):
            build.result = Result.failed
        # else, if we're finished, we can aggregate from results
        elif is_finished:
            if not job_list:
                build.result = Result.errored
                try:
                    with db.session.begin_nested():
                        db.session.add(
                            FailureReason(
                                repository_id=build.repository_id,
                                build_id=build.id,
                                reason=FailureReason.Reason.no_jobs,
                            )
                        )
                except IntegrityError as exc:
                    if "duplicate" not in str(exc):
                        raise
            elif not any(j for j in job_list if not j.allow_failure):
                build.result = Result.passed
            else:
                build.result = aggregate_result(
                    (j.result for j in job_list if not j.allow_failure)
                )
        # we should never get here as long we've got jobs and correct data
        else:
            build.result = Result.unknown

        if is_finished:
            build.status = Status.finished
            assert build.date_finished
        else:
            # ensure we dont set the status to finished unless it actually is
            new_status = aggregate_status((j.status for j in job_list))
            if build.status != new_status:
                build.status = new_status
            assert build.status != Status.finished

        db.session.add(build)
        db.session.commit()

        # we dont bother aggregating stats unless we're finished
        if build.status == Status.finished and not was_finished:
            for stat in AGGREGATED_BUILD_STATS:
                aggregate_stat_for_build(build, stat)
            db.session.commit()
            celery.delay("zeus.send_build_notifications", build_id=build.id)
