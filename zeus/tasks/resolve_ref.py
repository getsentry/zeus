from uuid import UUID

from zeus import auth
from zeus.api.schemas import BuildSchema
from zeus.config import celery, db
from zeus.constants import Result, Status
from zeus.exceptions import InvalidPublicKey, UnknownRevision
from zeus.models import Build, ChangeRequest
from zeus.pubsub.utils import publish
from zeus.utils import revisions


build_schema = BuildSchema()


@celery.task(max_retries=5, autoretry_for=(Exception,), acks_late=True, time_limit=60)
def resolve_ref_for_build(build_id: UUID):
    build = Build.query.unrestricted_unsafe().get(build_id)
    if not build:
        raise ValueError("Unable to find build with id = {}".format(build_id))

    auth.set_current_tenant(auth.RepositoryTenant(repository_id=build.repository_id))

    if not build.revision_sha:
        try:
            revision = revisions.identify_revision(
                build.repository, build.ref, with_vcs=True
            )
        except UnknownRevision:
            build.result = Result.errored
            build.status = Status.finished
            revision = None
        except InvalidPublicKey:
            revision = None

        if revision:
            build.revision_sha = revision.sha
            if not build.author_id and revision.authors:
                build.author = revision.authors[0]
                for author in revision.authors:
                    build.authors.append(author)
            if not build.label:
                build.label = revision.message.split("\n")[0]
        db.session.add(build)
        db.session.commit()

        data = build_schema.dump(build)
        publish("builds", "build.update", data)


@celery.task(max_retries=5, autoretry_for=(Exception,), acks_late=True, time_limit=60)
def resolve_ref_for_change_request(change_request_id: UUID):
    cr = ChangeRequest.query.unrestricted_unsafe().get(change_request_id)
    if not cr:
        raise ValueError(
            "Unable to find change request with id = {}".format(change_request_id)
        )

    auth.set_current_tenant(auth.RepositoryTenant(repository_id=cr.repository_id))

    if not cr.parent_revision_sha:
        try:
            revision = revisions.identify_revision(
                cr.repository, cr.parent_ref, with_vcs=True
            )
        except InvalidPublicKey:
            raise
        cr.parent_revision_sha = revision.sha
        if not cr.author_id and revision.authors:
            cr.author = revision.authors[0]
        db.session.add(cr)
        db.session.commit()

    if not cr.head_revision_sha and cr.head_ref:
        revision = revisions.identify_revision(
            cr.repository, cr.head_ref, with_vcs=True
        )
        cr.head_revision_sha = revision.sha
        db.session.add(cr)
        db.session.commit()
