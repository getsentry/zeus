from uuid import UUID

from zeus import auth
from zeus.config import celery
from zeus.constants import Result, Status
from zeus.models import Build
from zeus.notifications import email


@celery.task(name='zeus.tasks.send_build_notifications', max_retries=None)
def send_build_notifications(build_id: UUID):
    build = Build.query.get(build_id)
    if not build:
        raise ValueError('Unable to find build with id = {}'.format(build_id))

    auth.set_current_tenant(auth.Tenant(
        repository_ids=[build.repository_id]))

    # double check that the build is still finished and only send when
    # its failing
    if build.result != Result.failed or build.status != Status.finished:
        return

    email.send_email_notification(build=build)
