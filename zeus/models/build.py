from sqlalchemy import event
from sqlalchemy.sql import func, select

from zeus.config import db
from zeus.constants import Status, Result
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.types import Enum, GUID, JSONEncodedDict
from zeus.db.utils import model_repr


class Build(RepositoryBoundMixin, StandardAttributes, db.Model):
    """
    A single build linked to a source.

    Each Build contains many Jobs.
    """
    source_id = db.Column(
        GUID, db.ForeignKey('source.id', ondelete='CASCADE'), nullable=False, index=True
    )
    number = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String, nullable=False)
    status = db.Column(Enum(Status), nullable=False, default=Status.unknown)
    result = db.Column(Enum(Result), nullable=False, default=Result.unknown)
    date_started = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    date_finished = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    data = db.Column(JSONEncodedDict, nullable=True)
    provider = db.Column(db.String, nullable=True)
    external_id = db.Column(db.String(64), nullable=True)

    source = db.relationship('Source', innerjoin=True)
    stats = db.relationship(
        'ItemStat',
        foreign_keys='[ItemStat.item_id]',
        primaryjoin='ItemStat.item_id == Build.id',
        lazy='subquery',
        viewonly=True,
        uselist=True
    )

    __tablename__ = 'build'
    __table_args__ = (
        db.UniqueConstraint('repository_id', 'number', name='unq_build_number'),
        db.UniqueConstraint('repository_id', 'provider', 'external_id', name='unq_build_provider')
    )
    __repr__ = model_repr('number', 'status', 'result')


@event.listens_for(Build.repository_id, 'set', retval=False)
def set_number(target, value, oldvalue, initiator):
    if value is not None and target.number is None:
        target.number = select([func.next_item_value(value)])
    return value
