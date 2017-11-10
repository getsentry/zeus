from uuid import UUID

from zeus.config import celery
from zeus.constants import Result, Status
from zeus.models import Build
from zeus.notifications import email


@celery.task(max_retries=None)
def send_build_notifications(build_id: UUID):
    build = Build.query.get(build_id)
    assert build

    # double check that the build is still finished and only send when
    # its failing
    if build.result != Result.failed or build.status != Status.finished:
        return

    email.send_email_notification(build=build)
