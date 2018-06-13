from flask import request
from sqlalchemy.orm import contains_eager

from zeus.constants import Severity
from zeus.models import Job, StyleViolation, Revision
from zeus.utils.builds import fetch_build_for_revision

from .base_revision import BaseRevisionResource
from ..schemas import StyleViolationSchema

styleviolation_schema = StyleViolationSchema(many=True, strict=True)


class RevisionStyleViolationsResource(BaseRevisionResource):
    def get(self, revision: Revision):
        """
        Return a list of style violations for a given revision.
        """
        build = fetch_build_for_revision(revision.repository, revision)
        if not build:
            return self.respond(status=404)

        build_ids = [original.id for original in build.original]

        query = (
            StyleViolation.query.options(contains_eager("job"))
            .join(Job, StyleViolation.job_id == Job.id)
            .filter(Job.build_id.in_(build_ids))
        )

        severity = request.args.get("severity")
        if severity:
            try:
                query = query.filter(
                    StyleViolation.severity == getattr(Severity, severity)
                )
            except AttributeError:
                raise NotImplementedError

        query = query.order_by(
            (StyleViolation.severity == Severity.error).desc(),
            StyleViolation.filename.asc(),
            StyleViolation.lineno.asc(),
            StyleViolation.colno.asc(),
        )

        return self.paginate_with_schema(styleviolation_schema, query)
