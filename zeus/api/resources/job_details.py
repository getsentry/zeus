from zeus.config import celery, db
from zeus.constants import Result, Status
from zeus.models import Job
from zeus.utils import timezone
from zeus.utils.artifacts import has_unprocessed_artifacts

from .base_job import BaseJobResource
from ..schemas import JobSchema

job_schema = JobSchema()


class JobDetailsResource(BaseJobResource):
    def select_resource_for_update(self) -> bool:
        return False

    # TODO(dcramer): given we include the repository relation, its causing deadlocks
    # and we realistically dont need to lock that object
    # return self.is_mutation()

    def get(self, job: Job):
        """
        Return a job.
        """
        return self.respond_with_schema(job_schema, job)

    def put(self, job: Job):
        """
        Update a job.
        """
        result = self.schema_from_request(job_schema, partial=True)

        prev_status = job.status

        for key, value in result.items():
            if getattr(job, key) != value:
                setattr(job, key, value)

        if db.session.is_modified(job):
            job.date_updated = timezone.now()
            if job.status == Status.queued:
                job.date_started = None
                job.result = Result.unknown
            elif job.status == Status.in_progress and prev_status != Status.in_progress:
                # TODO(dcramer): this is effectively 'restart' on a job, and we need to
                # decide how Zeus should deal with it. We either could orphan/hide/remove the
                # current job, or alternatively we would want to truncate all of its children
                # which is fairly complex.
                if not result.get("date_started"):
                    job.date_started = timezone.now()
                if "result" not in result:
                    job.result = Result.unknown
            if (
                job.status == Status.finished
                and prev_status != job.status
                and not result.get("date_finished")
            ):
                job.date_finished = timezone.now()
                if not job.date_started:
                    job.date_started = job.date_created
            elif job.status != Status.finished:
                job.date_finished = None
            if job.status == Status.finished and has_unprocessed_artifacts(job):
                job.status = Status.collecting_results
            db.session.add(job)
            db.session.commit()

        celery.delay("zeus.aggregate_build_stats_for_job", job_id=job.id)

        return self.respond_with_schema(job_schema, job)
