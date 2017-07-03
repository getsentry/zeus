from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.orm import backref, relationship
from sqlalchemy.schema import Index

from zeus.config import db
from zeus.constants import Status, Result
from zeus.db.types import Enum, GUID, JSONEncodedDict


class Job(db.Model):
    """
    A single job, which is the actual execution unit for a build.
    """
    id = Column(GUID, primary_key=True, default=GUID.default_value)
    build_id = Column(GUID, ForeignKey(
        'build.id', ondelete='CASCADE'), nullable=False)
    status = Column(Enum(Status), nullable=False, default=Status.unknown)
    result = Column(Enum(Result), nullable=False, default=Result.unknown)
    date_started = Column(DateTime, nullable=True)
    date_finished = Column(DateTime, nullable=True)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)
    data = Column(JSONEncodedDict)

    build = relationship('Build',
                         backref=backref('jobs', order_by='Job.date_created'),
                         innerjoin=True)

    __tablename__ = 'job'
    __table_args__ = (
        Index('idx_job_build_id', 'build_id'),
    )
