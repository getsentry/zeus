from __future__ import absolute_import

import enum

from datetime import datetime
from sqlalchemy import Column, DateTime, String

from zeus.config import db
from zeus.db.types import Enum, GUID, JSONEncodedDict


class RepositoryBackend(enum.Enum):
    unknown = 0
    git = 1
    hg = 2

    _labels = {
        unknown: 'Unknown',
        git: 'git',
        hg: 'hg',
    }

    def __str__(self):
        return self._labels[self]


class RepositoryStatus(enum.Enum):
    inactive = 0
    active = 1
    importing = 2

    _labels = {
        inactive: 'Inactive',
        active: 'Active',
        importing: 'importing',
    }

    def __str__(self):
        return self._labels[self]


class Repository(db.Model):
    """
    Represents a single repository.
    """
    id = Column(GUID, primary_key=True, default=GUID.default_value)

    url = Column(String(200), nullable=False, unique=True)
    backend = Column(Enum(RepositoryBackend),
                     default=RepositoryBackend.unknown, nullable=False)
    status = Column(Enum(RepositoryStatus),
                    default=RepositoryStatus.inactive, nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)
    data = Column(JSONEncodedDict)

    __tablename__ = 'repository'
