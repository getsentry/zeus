from __future__ import absolute_import

import enum
import os.path

from datetime import datetime
from flask import current_app
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
    data = Column(JSONEncodedDict)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_update = Column(DateTime)
    last_update_attempt = Column(DateTime)

    __tablename__ = 'repository'

    def get_vcs(self):
        from zeus.models import ItemOption
        from zeus.vcs.git import GitVcs

        options = dict(
            db.session.query(
                ItemOption.name, ItemOption.value
            ).filter(
                ItemOption.item_id == self.id,
                ItemOption.name.in_([
                    'auth.username',
                ])
            )
        )

        kwargs = {
            'path': os.path.join(current_app.config['REPO_ROOT'], self.id.hex),
            'url': self.url,
            'username': options.get('auth.username'),
        }

        if self.backend == RepositoryBackend.git:
            return GitVcs(**kwargs)
        else:
            return None
