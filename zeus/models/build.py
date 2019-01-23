from sqlalchemy import event
from sqlalchemy.sql import func, select

from zeus.config import db
from zeus.constants import Status, Result
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.types import Enum, GUID, JSONEncodedDict
from zeus.db.utils import model_repr
from zeus.utils import timezone


class Build(RepositoryBoundMixin, StandardAttributes, db.Model):
    """
    A single build linked to a source.

    Each Build contains many Jobs.
    """

    source_id = db.Column(
        GUID, db.ForeignKey("source.id", ondelete="CASCADE"), nullable=False, index=True
    )
    number = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String, nullable=False)
    status = db.Column(Enum(Status), nullable=False, default=Status.unknown)
    result = db.Column(Enum(Result), nullable=False, default=Result.unknown)
    date_created = db.Column(
        db.TIMESTAMP(timezone=True),
        nullable=False,
        default=timezone.now,
        server_default=func.now(),
        index=True,
    )
    date_started = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    date_finished = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    data = db.Column(JSONEncodedDict, nullable=True)
    provider = db.Column(db.String, nullable=True)
    external_id = db.Column(db.String(64), nullable=True)
    hook_id = db.Column(
        GUID, db.ForeignKey("hook.id", ondelete="CASCADE"), nullable=True, index=True
    )
    url = db.Column(db.String, nullable=True)
    # author_id is inherited from Source.author_id, and is denormalized to speed up
    # "my builds" type of queries
    author_id = db.Column(
        GUID,
        db.ForeignKey("author.id", ondelete="SET NULL"),
        index=False,
        nullable=True,
    )

    author = db.relationship("Author")
    source = db.relationship("Source", innerjoin=True)
    hook = db.relationship("Hook")
    stats = db.relationship(
        "ItemStat",
        foreign_keys="[ItemStat.item_id]",
        primaryjoin="ItemStat.item_id == Build.id",
        viewonly=True,
        uselist=True,
    )

    __tablename__ = "build"
    __table_args__ = (
        db.UniqueConstraint("repository_id", "number", name="unq_build_number"),
        db.UniqueConstraint(
            "repository_id", "provider", "external_id", name="unq_build_provider"
        ),
        db.Index("idx_build_author_date", "author_id", "date_created"),
        db.Index("idx_build_outcomes", "status", "result", "date_created"),
    )
    __repr__ = model_repr("number", "status", "result")


@event.listens_for(Build.repository_id, "set", retval=False)
def set_number(target, value, oldvalue, initiator):
    if value is not None and target.number is None:
        target.number = select([func.next_item_value(value)])
    return value
