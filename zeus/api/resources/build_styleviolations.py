from flask import request

from zeus.config import db
from zeus.constants import Severity
from zeus.models import Job, Build, StyleViolation

from .base_build import BaseBuildResource
from ..schemas import StyleViolationSchema

styleviolation_schema = StyleViolationSchema(many=True, strict=True)


class BuildStyleViolationsResource(BaseBuildResource):
    def get(self, build: Build):
        """
        Return a list of style violations for a given build.
        """
        job_query = db.session.query(Job.id).filter(Job.build_id == build.id)

        result = request.args.get("allowed_failures")
        if result == "false":
            job_query = job_query.filter(Job.allow_failure == False)  # NOQA
        job_ids = job_query.subquery()

        query = StyleViolation.query.filter(StyleViolation.job_id.in_(job_ids))

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
