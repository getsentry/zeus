from flask import request
from sqlalchemy import or_

from zeus.config import db
from zeus.db.func import array_agg_row
from zeus.models import Job, Revision, FailureReason
from zeus.utils.builds import fetch_build_for_revision

from .base_revision import BaseRevisionResource
from ..schemas import AggregateFailureReasonSchema

failurereasons_schema = AggregateFailureReasonSchema(many=True)


class RevisionFailuresResource(BaseRevisionResource):
    def get(self, revision: Revision):
        """
        Return a list of failure reasons for a given revision.
        """
        build = fetch_build_for_revision(revision)
        if not build:
            return self.respond(status=404)

        build_ids = [original.id for original in build.original]

        job_query = db.session.query(Job.id).filter(Job.build_id.in_(build_ids))

        result = request.args.get("allowed_failures")
        if result == "false":
            job_query = job_query.filter(Job.allow_failure == False)  # NOQA
        job_ids = job_query.subquery()

        query = (
            db.session.query(
                FailureReason.reason,
                array_agg_row(FailureReason.id, FailureReason.job_id).label("runs"),
            )
            .filter(
                or_(
                    FailureReason.job_id.in_(job_ids),
                    FailureReason.build_id.in_(build_ids),
                )
            )
            .group_by(FailureReason.reason)
        )

        query = query.order_by(FailureReason.reason.asc())

        return self.paginate_with_schema(failurereasons_schema, query)
