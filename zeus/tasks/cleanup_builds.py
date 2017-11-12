from datetime import timedelta

from zeus.config import celery, db
from zeus.constants import Result, Status
from zeus.models import Build, Job
from zeus.utils import timezone

from .aggregate_job_stats import aggregate_build_stats


@celery.task(name='zeus.cleanup_builds', max_retries=None)
def cleanup_builds():
    # first we timeout any jobs which have been sitting for far too long
    Job.query.unrestricted_unsafe().filter(
        Job.status == Status.in_progress,
        Job.date_started < timezone.now() - timedelta(hours=1),
    ).update({
        'status': Status.finished,
        'result': Result.errored,
        'date_finished': timezone.now(),
    })
    db.session.commit()

    queryset = Build.query.unrestricted_unsafe().filter(
        Build.status != Status.finished,
        ~Job.query.filter(
            Job.build_id == Build.id,
            Job.status != Status.finished,
        ).exists()
    )

    for build in queryset:
        aggregate_build_stats(build_id=build.id)
