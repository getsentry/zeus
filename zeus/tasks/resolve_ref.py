from uuid import UUID

from zeus.api.schemas import BuildSchema
from zeus.config import celery, db
from zeus.models import Build, ChangeRequest
from zeus.pubsub.utils import publish
from zeus.utils import revisions

build_schema = BuildSchema()


@celery.task(max_retries=5, autoretry_for=(Exception,), acks_late=True, time_limit=60)
def resolve_ref_for_build(build_id: UUID):
    build = Build.query.get(build_id)
    if not build.revision_sha:
        revision = revisions.identify(build.repository, build.ref, with_vcs=True)
        build.revision_sha = revision.sha
        db.session.add(build)
        db.session.commit()

        data = build_schema.dump(build)
        publish("builds", "build.update", data)


@celery.task(max_retries=5, autoretry_for=(Exception,), acks_late=True, time_limit=60)
def resolve_ref_for_change_request(change_request_id: UUID):
    cr = ChangeRequest.query.get(change_request_id)

    if not cr.head_revision_sha:
        revision = revisions.identify(cr.repository, cr.head_ref, with_vcs=True)
        cr.head_revision_sha = revision.sha
        db.session.add(cr)
        db.session.commit()

    if not cr.parent_revision_sha:
        revision = revisions.identify(cr.repository, cr.parent_ref, with_vcs=True)
        cr.parent_revision_sha = revision.sha
        db.session.add(cr)
        db.session.commit()
