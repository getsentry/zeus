from sqlalchemy.exc import IntegrityError
from typing import Optional
from uuid import UUID

from zeus import auth
from zeus.api.schemas import BuildSchema
from zeus.config import celery, db
from zeus.constants import Result, Status
from zeus.exceptions import InvalidPublicKey, UnknownRevision
from zeus.models import Build, ChangeRequest, FailureReason, Revision
from zeus.pubsub.utils import publish
from zeus.utils import revisions


build_schema = BuildSchema()


@celery.task(max_retries=5, autoretry_for=(Exception,), acks_late=True, time_limit=60)
def resolve_ref_for_build(build_id: UUID):
    with db.session.begin_nested():
        build = (
            Build.query.unrestricted_unsafe().with_for_update(nowait=True).get(build_id)
        )
        if not build:
            raise ValueError("Unable to find build with id = {}".format(build_id))

        if build.revision_sha:
            return

        auth.set_current_tenant(
            auth.RepositoryTenant(repository_id=build.repository_id)
        )

        revision: Optional[Revision] = None
        try:
            revision = revisions.identify_revision(
                build.repository, build.ref, with_vcs=True
            )
        except UnknownRevision:
            build.result = Result.errored
            build.status = Status.finished
            try:
                with db.session.begin_nested():
                    db.session.add(
                        FailureReason(
                            repository_id=build.repository_id,
                            build_id=build.id,
                            reason=FailureReason.Reason.unresolvable_ref,
                        )
                    )
                    db.session.flush()
            except IntegrityError as exc:
                if "duplicate" not in str(exc):
                    raise

        except InvalidPublicKey:
            pass

        if revision:
            build.revision_sha = revision.sha
            if not build.authors and revision.authors:
                build.authors = revision.authors
            if not build.label:
                build.label = revision.message.split("\n")[0]
        db.session.add(build)

    data = build_schema.dump(build)
    publish("builds", "build.update", data)


@celery.task(max_retries=5, autoretry_for=(Exception,), acks_late=True, time_limit=60)
def resolve_ref_for_change_request(change_request_id: UUID):
    with db.session.begin_nested():
        cr = (
            ChangeRequest.query.unrestricted_unsafe()
            .with_for_update(nowait=True)
            .get(change_request_id)
        )
        if not cr:
            raise ValueError(
                "Unable to find change request with id = {}".format(change_request_id)
            )

        auth.set_current_tenant(auth.RepositoryTenant(repository_id=cr.repository_id))

        if not cr.parent_revision_sha and cr.parent_ref:
            try:
                revision = revisions.identify_revision(
                    cr.repository, cr.parent_ref, with_vcs=True
                )
            except InvalidPublicKey:
                raise
            cr.parent_revision_sha = revision.sha
            db.session.add(cr)

        if not cr.head_revision_sha and cr.head_ref:
            revision = revisions.identify_revision(
                cr.repository, cr.head_ref, with_vcs=True
            )
            cr.head_revision_sha = revision.sha
            if not cr.authors and revision.authors:
                cr.authors = revision.authors
            db.session.add(cr)
