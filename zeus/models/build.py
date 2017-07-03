from __future__ import absolute_import

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from zeus.config import db
from zeus.constants import Status, Result
from zeus.db.types import Enum, GUID, JSONEncodedDict


class Build(db.Model):
    """
    A single build linked to a source.

    Each Build contains many Jobs.
    """
    id = Column(GUID, primary_key=True, default=GUID.default_value)
    repository_id = Column(GUID, ForeignKey(
        'repository.id', ondelete='CASCADE'), nullable=False)
    source_id = Column(GUID, ForeignKey(
        'source.id', ondelete='CASCADE'), nullable=False)
    status = Column(Enum(Status), nullable=False, default=Status.unknown)
    result = Column(Enum(Result), nullable=False, default=Result.unknown)
    date_started = Column(DateTime, nullable=True)
    date_finished = Column(DateTime, nullable=True)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)
    data = Column(JSONEncodedDict)

    repositoryroject = relationship('Repository', innerjoin=True)
    source = relationship('Source', innerjoin=True)

    __tablename__ = 'build'
    __table_args__ = (
        Index('idx_build_repository_id', 'repository_id'),
        Index('idx_build_source_id', 'source_id'),
    )
