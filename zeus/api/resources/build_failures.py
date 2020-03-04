from zeus.config import db
from zeus.db.func import array_agg_row
from zeus.models import Build, FailureReason

from .base_build import BaseBuildResource
from ..schemas import AggregateFailureReasonSchema

failurereasons_schema = AggregateFailureReasonSchema(many=True)


class BuildFailuresResource(BaseBuildResource):
    def get(self, build: Build):
        """
        Return a list of failure reasons for a given build.
        """
        query = (
            db.session.query(
                FailureReason.reason,
                array_agg_row(FailureReason.id, FailureReason.job_id).label("runs"),
            )
            .filter(FailureReason.build_id == build.id)
            .group_by(FailureReason.reason)
        )

        query = query.order_by(FailureReason.reason.asc())

        return self.paginate_with_schema(failurereasons_schema, query)
