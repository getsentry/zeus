from sqlalchemy import event
from sqlalchemy.sql import func, select

from zeus.config import db
from zeus.constants import Status, Result
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.types import Enum, GUID, JSONEncodedDict
from zeus.db.utils import model_repr
from zeus.utils import timezone


class Job(RepositoryBoundMixin, StandardAttributes, db.Model):
    """
    A single job, which is the actual execution unit for a build.
    """

    id = db.Column(GUID, primary_key=True, default=GUID.default_value)
    build_id = db.Column(
        GUID, db.ForeignKey("build.id", ondelete="CASCADE"), nullable=False, index=True
    )
    number = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String, nullable=True)
    status = db.Column(Enum(Status), nullable=False, default=Status.unknown)
    result = db.Column(Enum(Result), nullable=False, default=Result.unknown)
    allow_failure = db.Column(
        db.Boolean, nullable=False, default=False, server_default="0"
    )
    date_started = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    date_updated = db.Column(
        db.TIMESTAMP(timezone=True), nullable=True, onupdate=timezone.now
    )
    date_finished = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    data = db.Column(JSONEncodedDict, nullable=True)
    provider = db.Column(db.String, nullable=True)
    external_id = db.Column(db.String(64), nullable=True)
    hook_id = db.Column(
        GUID, db.ForeignKey("hook.id", ondelete="CASCADE"), nullable=True, index=True
    )
    url = db.Column(db.String, nullable=True)

    build = db.relationship(
        "Build", backref=db.backref("jobs", order_by="Job.date_created"), innerjoin=True
    )
    hook = db.relationship("Hook")
    stats = db.relationship(
        "ItemStat",
        foreign_keys="[ItemStat.item_id]",
        primaryjoin="ItemStat.item_id == Job.id",
        viewonly=True,
        uselist=True,
    )
    failures = db.relationship(
        "FailureReason",
        foreign_keys="[FailureReason.job_id]",
        primaryjoin="FailureReason.job_id == Job.id",
        viewonly=True,
        uselist=True,
    )

    __tablename__ = "job"
    __table_args__ = (
        db.UniqueConstraint("build_id", "number", name="unq_job_number"),
        db.UniqueConstraint(
            "build_id", "provider", "external_id", name="unq_job_provider"
        ),
        db.Index("idx_job_finished", "repository_id", "status", "date_finished"),
    )
    __repr__ = model_repr("build_id", "number", "status", "result")


@event.listens_for(Job.build_id, "set", retval=False)
def set_number(target, value, oldvalue, initiator):
    if value is not None and target.number is None:
        target.number = select([func.next_item_value(value)])
    return value
