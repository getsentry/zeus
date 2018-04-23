from flask import request
from sqlalchemy.orm import contains_eager

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
        query = StyleViolation.query.options(contains_eager("job")).join(
            Job, StyleViolation.job_id == Job.id
        ).filter(
            Job.build_id == build.id
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
