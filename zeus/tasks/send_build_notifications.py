from datetime import timedelta
from flask import current_app
from uuid import UUID

from zeus import auth
from zeus.config import celery
from zeus.constants import Result, Status
from zeus.models import Build
from zeus.notifications import email
from zeus.utils import timezone


@celery.task(
    name="zeus.send_build_notifications", max_retries=None, autoretry_for=(Exception,)
)
def send_build_notifications(build_id: UUID, time_limit=30):
    build = Build.query.unrestricted_unsafe().get(build_id)
    if not build:
        raise ValueError("Unable to find build with id = {}".format(build_id))

    if not build.date_started:
        current_app.logger.warn(
            "send_build_notifications: build %s missing date_started", build_id
        )
        return

    if not build.date_finished:
        current_app.logger.warn(
            "send_build_notifications: build %s missing date_finished", build_id
        )
        return

    auth.set_current_tenant(auth.RepositoryTenant(repository_id=build.repository_id))

    # double check that the build is still finished and only send when
    # its failing
    if build.result != Result.failed or build.status != Status.finished:
        current_app.logger.warn(
            "send_build_notifications: build %s not marked as failed", build_id
        )
        return

    if build.date_finished < timezone.now() - timedelta(days=1):
        current_app.logger.warn(
            "send_build_notifications: build %s fimished a long time ago", build_id
        )
        return

    if build.date_started < timezone.now() - timedelta(days=7):
        current_app.logger.warn(
            "send_build_notifications: build %s started a long time ago", build_id
        )
        return

    email.send_email_notification(build=build)
