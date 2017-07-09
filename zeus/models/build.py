from datetime import datetime

from zeus.config import db
from zeus.constants import Status, Result
from zeus.db.mixins import RepositoryBoundMixin
from zeus.db.types import Enum, GUID, JSONEncodedDict
from zeus.db.utils import model_repr


class Build(RepositoryBoundMixin, db.Model):
    """
    A single build linked to a source.

    Each Build contains many Jobs.
    """
    id = db.Column(GUID, primary_key=True, default=GUID.default_value)
    source_id = db.Column(
        GUID, db.ForeignKey('source.id', ondelete='CASCADE'), nullable=False, index=True
    )
    status = db.Column(Enum(Status), nullable=False, default=Status.unknown)
    result = db.Column(Enum(Result), nullable=False, default=Result.unknown)
    date_started = db.Column(db.DateTime, nullable=True)
    date_finished = db.Column(db.DateTime, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data = db.Column(JSONEncodedDict)

    source = db.relationship('Source', innerjoin=True)

    __tablename__ = 'build'
    __repr__ = model_repr('repository_id', 'source_id', 'status', 'result')
