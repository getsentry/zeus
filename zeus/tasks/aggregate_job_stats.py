from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from uuid import UUID

from zeus import auth
from zeus.config import celery, db, redis
from zeus.constants import Result, Status
from zeus.db.utils import create_or_update
from zeus.models import (Artifact, Build, FailureReason,
                         FileCoverage, ItemStat, Job, TestCase)
from zeus.notifications.email import send_email_notification
from zeus.utils import timezone
from zeus.utils.aggregation import aggregate_result, aggregate_status, safe_agg

AGGREGATED_BUILD_STATS = (
    'tests.count', 'tests.duration', 'tests.failures',
)


# TODO(dcramer): put a lock around this
@celery.task(max_retries=None)
def aggregate_build_stats_for_job(job_id: UUID):
    """
    Given a job, aggregate its data upwards into the Build.abs

    This should generally be fired upon a job's completion, or
    alternatively it can be used to repair aggregate data.
    """
    lock_key = 'job:{job_id}'.format(
        job_id=job_id,
    )
    with redis.lock(lock_key):
        job = Job.query.unrestricted_unsafe().with_for_update().filter(
            Job.id == job_id,
        ).first()
        if not job:
            raise ValueError

        auth.set_current_tenant(auth.Tenant(
            repository_ids=[job.repository_id]))

        # we need to handle the race between when the mutations were made to <Job> and
        # when the only remaining artifact may have finished processing
        if job.status == Status.collecting_results and not has_unprocessed_artifacts(job.id):
            job.status = Status.finished
            if not job.date_finished:
                job.date_finished = timezone.now()
            db.session.add(job)
            db.session.commit()

        # record any job-specific stats that might not have been taken care elsewhere
        # (we might want to move TestResult's stats here as well)
        if job.status == Status.finished:
            record_test_stats(job.id)
            record_failure_reasons(job)

    lock_key = 'aggstatsbuild:{build_id}'.format(
        build_id=job.build_id.hex,
    )
    with redis.lock(lock_key):
        record_coverage_stats(job.build_id)
        aggregate_build_stats(job.build_id)


def aggregate_stat_for_build(build: Build, name: str, func_=func.sum):
    """
    Aggregates a single stat for all jobs the given build.
    """
    value = db.session.query(
        func.coalesce(func_(ItemStat.value), 0),
    ).filter(
        ItemStat.item_id.in_(db.session.query(Job.id).filter(
            Job.build_id == build.id,
        )),
        ItemStat.name == name,
    ).as_scalar()

    create_or_update(
        model=ItemStat,
        where={
            'item_id': build.id,
            'name': name,
        },
        values={'value': value},
    )


def has_unprocessed_artifacts(job_id: UUID):
    return db.session.query(
        Artifact.query.filter(
            Artifact.status != Status.finished,
            Artifact.job_id == job_id,
        ).exists()
    ).scalar()


def record_failure_reasons(job: Job):
    has_failures = db.session.query(
        TestCase.query.filter(
            TestCase.job_id == job.id,
            TestCase.result == Result.failed,
        ).exists()
    ).scalar()
    any_failures = False

    if has_failures:
        any_failures = True
        try:
            with db.session.begin_nested():
                db.session.add(
                    FailureReason(
                        job_id=job.id,
                        repository_id=job.repository_id,
                        reason=FailureReason.Reason.failing_tests,
                    )
                )
        except IntegrityError:
            pass

    if any_failures and job.result == Result.passed:
        job.result = Result.failed
        db.session.add(job)

    db.session.flush()


def record_test_stats(job_id: UUID):
    create_or_update(
        ItemStat,
        where={
            'item_id': job_id,
            'name': 'tests.count',
        },
        values={
            'value':
            db.session.query(func.count(TestCase.id)).filter(
                TestCase.job_id == job_id,
            ).as_scalar(),
        }
    )
    create_or_update(
        ItemStat,
        where={
            'item_id': job_id,
            'name': 'tests.failures',
        },
        values={
            'value':
            db.session.query(func.count(TestCase.id)).filter(
                TestCase.job_id == job_id,
                TestCase.result == Result.failed,
            ).as_scalar(),
        }
    )
    create_or_update(
        ItemStat,
        where={
            'item_id': job_id,
            'name': 'tests.duration',
        },
        values={
            'value':
            db.session.query(func.coalesce(func.sum(TestCase.duration), 0)).filter(
                TestCase.job_id == job_id,
            ).as_scalar(),
        }
    )
    db.session.flush()


def record_coverage_stats(build_id: UUID):
    """
    Aggregates all FileCoverage stats for the given build.
    """
    coverage_stats = db.session.query(
        func.sum(FileCoverage.lines_covered).label('coverage.lines_covered'),
        func.sum(FileCoverage.lines_uncovered).label(
            'coverage.lines_uncovered'),
        func.sum(FileCoverage.diff_lines_covered).label(
            'coverage.diff_lines_covered'),
        func.sum(FileCoverage.diff_lines_uncovered).label(
            'coverage.diff_lines_uncovered'),
    ).filter(
        FileCoverage.build_id == build_id,
    ).group_by(
        FileCoverage.build_id,
    ).first()

    # TODO(dcramer): it'd be safer if we did this query within SQL
    stat_list = (
        'coverage.lines_covered', 'coverage.lines_uncovered', 'coverage.diff_lines_covered',
        'coverage.diff_lines_uncovered',
    )
    if not any(getattr(coverage_stats, n, None) is not None for n in stat_list):
        ItemStat.query.filter(
            ItemStat.item_id == build_id,
            ItemStat.name.in_(stat_list)
        ).delete(synchronize_session=False)
    else:
        for name in stat_list:
            create_or_update(
                model=ItemStat,
                where={
                    'item_id': build_id,
                    'name': name,
                },
                values={
                    'value': getattr(coverage_stats, name, 0) or 0,
                },
            )


def aggregate_build_stats(build_id: UUID):
    """
    Updates various denormalized / aggregate attributes on Build per its
    jobs. These attributes include start and completion dates, as well as
    the status and result.
    """
    # now we pull in the entirety of the build's data to aggregate state upward
    build = Build.query.with_for_update().get(build_id)
    if not build:
        raise ValueError

    job_list = Job.query.filter(Job.build_id == build.id)

    was_finished = build.status == Status.finished
    is_finished = all(p.status == Status.finished for p in job_list)

    # ensure build's dates are reflective of jobs
    build.date_started = safe_agg(
        min, (j.date_started for j in job_list if j.date_started))

    if is_finished:
        build.date_finished = safe_agg(
            max, (j.date_finished for j in job_list if j.date_finished))
    else:
        build.date_finished = None

    # if theres any failure, the build failed
    if any(j.result is Result.failed for j in job_list if not j.allow_failure):
        build.result = Result.failed
    # else, if we're finished, we can aggregate from results
    elif is_finished:
        build.result = aggregate_result(
            (j.result for j in job_list if not j.allow_failure))
        # special case when there were only 'allowed failures'
        if build.result == Result.unknown:
            if not job_list:
                # if no jobs were run we should fail
                build.result = Result.failed
            else:
                build.result = Result.passed
    # we should never get here as long we've got jobs and correct data
    else:
        build.result = Result.unknown

    if is_finished:
        build.status = Status.finished
    else:
        # ensure we dont set the status to finished unless it actually is
        new_status = aggregate_status((j.status for j in job_list))
        if build.status != new_status:
            build.status = new_status

    db.session.add(build)
    db.session.commit()

    # we dont bother aggregating stats unless we're finished
    if is_finished and not was_finished:
        for stat in AGGREGATED_BUILD_STATS:
            aggregate_stat_for_build(build, stat)
        send_email_notification(build)
