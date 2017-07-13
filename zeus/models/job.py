from sqlalchemy import event
from sqlalchemy.sql import func, select

from datetime import datetime

from zeus.config import db
from zeus.constants import Status, Result
from zeus.db.mixins import RepositoryBoundMixin
from zeus.db.types import Enum, GUID, JSONEncodedDict
from zeus.db.utils import model_repr


class Job(RepositoryBoundMixin, db.Model):
    """
    A single job, which is the actual execution unit for a build.
    """
    id = db.Column(GUID, primary_key=True, default=GUID.default_value)
    build_id = db.Column(
        GUID, db.ForeignKey('build.id', ondelete='CASCADE'), nullable=False, index=True
    )
    number = db.Column(db.Integer, nullable=False)
    status = db.Column(Enum(Status), nullable=False, default=Status.unknown)
    result = db.Column(Enum(Result), nullable=False, default=Result.unknown)
    date_started = db.Column(db.DateTime, nullable=True)
    date_finished = db.Column(db.DateTime, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data = db.Column(JSONEncodedDict, nullable=True)
    provider = db.Column(db.String, nullable=True)
    external_id = db.Column(db.String(64), nullable=True)

    build = db.relationship(
        'Build', backref=db.backref('jobs', order_by='Job.date_created'), innerjoin=True
    )
    stats = db.relationship(
        'ItemStat',
        foreign_keys='[ItemStat.item_id]',
        primaryjoin='ItemStat.item_id == Job.id',
        lazy='subquery',
        viewonly=True,
        uselist=True
    )

    __tablename__ = 'job'
    __table_args__ = (
        db.UniqueConstraint('build_id', 'number', name='unq_job_number'),
        db.UniqueConstraint('build_id', 'provider', 'external_id', name='unq_job_provider')
    )
    __repr__ = model_repr('build_id', 'number', 'status', 'result')


@event.listens_for(Job.build_id, 'set', retval=False)
def set_number(target, value, oldvalue, initiator):
    if value is not None and target.number is None:
        target.number = select([func.next_item_value(value)])
    return value
