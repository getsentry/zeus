from __future__ import absolute_import, division

import enum

from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.types import GUID, StrEnum
from zeus.db.utils import model_repr


class FailureReason(RepositoryBoundMixin, StandardAttributes, db.Model):
    class Reason(enum.Enum):
        failing_tests = "failing_tests"
        missing_tests = "missing_tests"
        no_jobs = "no_jobs"
        unresolvable_ref = "unresolvable_ref"
        timeout = "timeout"
        internal_error = "internal_error"

    build_id = db.Column(
        GUID, db.ForeignKey("build.id", ondelete="CASCADE"), nullable=True
    )
    job_id = db.Column(GUID, db.ForeignKey("job.id", ondelete="CASCADE"), nullable=True)
    reason = db.Column(StrEnum(Reason), nullable=False)

    build = db.relationship("Build")
    job = db.relationship("Job")

    __tablename__ = "failurereason"
    __table_args__ = (
        db.UniqueConstraint(
            "build_id", "job_id", "reason", name="unq_failurereason_key"
        ),
        db.Index(
            "unq_failurereason_buildonly",
            build_id,
            reason,
            unique=True,
            postgresql_where=job_id.is_(None),
        ),
    )
    __repr__ = model_repr("reason")
