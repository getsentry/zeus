from celery import shared_task
from sqlalchemy.sql import func
from uuid import UUID

from zeus import auth
from zeus.config import db, redis
from zeus.constants import Result, Status
from zeus.db.utils import create_or_update
from zeus.models import Build, FileCoverage, ItemStat, Job
from zeus.utils.aggregation import aggregate_result, aggregate_status, safe_agg

STATS = (
    'tests.count', 'tests.duration', 'tests.failures', 'coverage.lines_covered',
    'coverage.lines_uncovered', 'coverage.diff_lines_covered', 'coverage.diff_lines_uncovered',
)


@shared_task
def aggregate_build_stats_for_job(job_id: UUID):
    """
    Given a job, aggregate its data upwards into the Build.abs

    This should generally be fired upon a job's completion, or
    alternatively it can be used to repair aggregate data.
    """
    job = Job.query.unrestricted_unsafe().filter(
        Job.id == job_id,
    ).first()
    if not job:
        raise ValueError

    auth.set_current_tenant(auth.Tenant(repository_ids=[job.repository_id]))

    # record any job-specific stats that might not have been taken care elsewhere
    # (we might want to move TestResult's stats here as well, or move coverage's
    # stats elsewhere)
    record_coverage_stats(job)

    lock_key = 'aggstatsbuild:{build_id}'.format(
        build_id=job.build_id.hex,
    )
    with redis.lock(lock_key):
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


def record_coverage_stats(job: Job):
    """
    Aggregates all FileCoverage stats for the given job.
    """
    coverage_stats = db.session.query(
        func.sum(FileCoverage.lines_covered).label('coverage.lines_covered'),
        func.sum(FileCoverage.lines_uncovered).label('coverage.lines_uncovered'),
        func.sum(FileCoverage.diff_lines_covered).label('coverage.diff_lines_covered'),
        func.sum(FileCoverage.diff_lines_uncovered).label('coverage.diff_lines_uncovered'),
    ).filter(
        FileCoverage.job_id == job.id,
    ).group_by(
        FileCoverage.job_id,
    ).first()

    # TODO(dcramer): it'd be safer if we did this query within SQL
    stat_list = (
        'coverage.lines_covered', 'coverage.lines_uncovered', 'coverage.diff_lines_covered',
        'coverage.diff_lines_uncovered',
    )
    for name in stat_list:
        create_or_update(
            model=ItemStat,
            where={
                'item_id': job.id,
                'name': name,
            },
            values={'value': getattr(coverage_stats, name, 0) or 0},
        )


def aggregate_build_stats(build_id: UUID):
    """
    Updates various denormalized / aggregate attributes on Build per its
    jobs. These attributes include start and completion dates, as well as
    the status and result.
    """
    # now we pull in the entirety of the build's data to aggregate state upward
    build = Build.query.get(build_id)
    if not build:
        raise ValueError

    job_list = Job.query.filter(Job.build_id == build.id)

    is_finished = any(p.status == Status.finished for p in job_list)

    # ensure build's dates are reflective of jobs
    build.date_started = safe_agg(min, (j.date_started for j in job_list if j.date_started))

    if is_finished:
        build.date_finished = safe_agg(max, (j.date_finished for j in job_list if j.date_finished))
    else:
        build.date_finished = None

    # if theres any failure, the build failed
    if any(j.result is Result.failed for j in job_list):
        build.result = Result.failed
    # else, if we're finished, we can aggregate from results
    elif is_finished:
        build.result = aggregate_result((j.result for j in job_list))
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

    if db.session.is_modified(build):
        db.session.add(build)
        db.session.commit()

    # we dont bother aggregating stats unless we're finished
    if is_finished:
        for stat in STATS:
            aggregate_stat_for_build(build, stat)
