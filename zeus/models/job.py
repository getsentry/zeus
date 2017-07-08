from datetime import datetime

from zeus.config import db
from zeus.constants import Status, Result
from zeus.db.mixins import RepositoryBoundMixin
from zeus.db.types import Enum, GUID, JSONEncodedDict


class Job(RepositoryBoundMixin, db.Model):
    """
    A single job, which is the actual execution unit for a build.
    """
    id = db.Column(GUID, primary_key=True, default=GUID.default_value)
    build_id = db.Column(
        GUID, db.ForeignKey('build.id', ondelete='CASCADE'), nullable=False, index=True
    )
    status = db.Column(Enum(Status), nullable=False, default=Status.unknown)
    result = db.Column(Enum(Result), nullable=False, default=Result.unknown)
    date_started = db.Column(db.DateTime, nullable=True)
    date_finished = db.Column(db.DateTime, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data = db.Column(JSONEncodedDict)

    build = db.relationship(
        'Build', backref=db.backref('jobs', order_by='Job.date_created'), innerjoin=True
    )

    __tablename__ = 'job'
