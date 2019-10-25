from datetime import timedelta
from uuid import UUID

from zeus import auth
from zeus.config import celery
from zeus.constants import Result, Status
from zeus.models import Build
from zeus.notifications import email
from zeus.utils import timezone


@celery.task(
    name="zeus.tasks.send_build_notifications",
    max_retries=None,
    autoretry_for=(Exception,),
)
def send_build_notifications(build_id: UUID, time_limit=30):
    build = Build.query.unrestricted_unsafe().get(build_id)
    if not build:
        raise ValueError("Unable to find build with id = {}".format(build_id))

    auth.set_current_tenant(auth.RepositoryTenant(repository_id=build.repository_id))

    # double check that the build is still finished and only send when
    # its failing
    if build.result != Result.failed or build.status != Status.finished:
        return

    if build.date_finished < timezone.now() - timedelta(days=1):
        return

    if build.date_started < timezone.now() - timedelta(days=7):
        return

    email.send_email_notification(build=build)
