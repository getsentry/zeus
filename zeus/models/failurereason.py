from __future__ import absolute_import, division

import enum

from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.types import GUID, StrEnum


class FailureReason(RepositoryBoundMixin, StandardAttributes, db.Model):
    __tablename__ = 'failurereason'
    __table_args__ = (db.UniqueConstraint(
        'job_id', 'reason', name='unq_failurereason_key'), )

    class Reason(enum.Enum):
        failing_tests = 'failing_tests'
        missing_tests = 'missing_tests'

    job_id = db.Column(GUID, db.ForeignKey(
        'job.id', ondelete="CASCADE"), nullable=False)
    reason = db.Column(StrEnum(Reason), nullable=False)

    job = db.relationship('Job')
