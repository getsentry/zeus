from datetime import timedelta

from zeus.config import celery, db
from zeus.constants import Result, Status
from zeus.models import Artifact, Build, Job
from zeus.utils import timezone

from .aggregate_job_stats import aggregate_build_stats
from .process_artifact import process_artifact


@celery.task(name='zeus.cleanup_builds', max_retries=None)
def cleanup_builds():
    # find any artifacts which seemingly are stuck (not enqueued)
    queryset = Artifact.query.unrestricted_unsafe().filter(
        Artifact.status == Status.queued,
        Artifact.date_created < timezone.now() - timedelta(minutes=15),
    )
    # HACK(dramer): ensure we dont double process this artifact
    queryset.update({
        'status': Artifact.in_progress,
    })
    db.session.flush()
    for result in queryset:
        process_artifact.delay(artifact_id=result.id)

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
