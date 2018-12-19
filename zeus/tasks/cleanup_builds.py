from datetime import timedelta

from zeus.config import queue, db
from zeus.constants import Result, Status
from zeus.models import Artifact, Build, Job
from zeus.utils import timezone

from .aggregate_job_stats import aggregate_build_stats
from .process_artifact import process_artifact


@queue.task(name="zeus.cleanup_builds")
def cleanup_builds():
    # find any artifacts which seemingly are stuck (not enqueued)
    queryset = Artifact.query.unrestricted_unsafe().filter(
        Artifact.status != Status.finished,
        Artifact.date_updated < timezone.now() - timedelta(minutes=15),
    )
    for result in queryset:
        Artifact.query.unrestricted_unsafe().filter(
            Artifact.status != Status.finished, Artifact.id == result.id
        ).update({"date_updated": timezone.now()})
        db.session.flush()
        process_artifact(artifact_id=result.id)

    # first we timeout any jobs which have been sitting for far too long
    Job.query.unrestricted_unsafe().filter(
        Job.status != Status.finished,
        Job.date_updated < timezone.now() - timedelta(hours=1),
    ).update(
        {
            "status": Status.finished,
            "result": Result.errored,
            "date_updated": timezone.now(),
            "date_finished": timezone.now(),
        }
    )
    db.session.commit()

    queryset = Build.query.unrestricted_unsafe().filter(
        Build.status != Status.finished,
        ~Job.query.filter(
            Job.build_id == Build.id, Job.status != Status.finished
        ).exists(),
    )
    for build in queryset:
        aggregate_build_stats(build_id=build.id)
