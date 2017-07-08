import enum
import os.path
import sqlalchemy

from datetime import datetime
from flask import current_app
from sqlalchemy import Column, DateTime, String

from zeus.config import db
from zeus.db.types import Enum, GUID, JSONEncodedDict


class RepositoryBackend(enum.Enum):
    unknown = 0
    git = 1

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


class RepositoryAccessBoundQuery(db.Query):
    current_constrained = True

    def get(self, ident):
        # override get() so that the flag is always checked in the
        # DB as opposed to pulling from the identity map. - this is optional.
        return db.Query.get(self.populate_existing(), ident)

    def __iter__(self):
        return db.Query.__iter__(self.constrained())

    def from_self(self, *ent):
        # override from_self() to automatically apply
        # the criterion too.   this works with count() and
        # others.
        return db.Query.from_self(self.constrained(), *ent)

    def constrained(self):
        from zeus.auth import get_current_tenant

        if not self.current_constrained:
            return self

        mzero = self._mapper_zero()
        if mzero is not None:
            tenant = get_current_tenant()
            if tenant.repository_ids:
                return self.enable_assertions(False).filter(
                    mzero.class_.id.in_(tenant.repository_ids))
            else:
                return self.enable_assertions(False).filter(sqlalchemy.sql.false())
        return self

    def unrestricted_unsafe(self):
        rv = self._clone()
        rv.current_constrained = False
        return rv


class Repository(db.Model):
    """
    Represents a single repository.
    """
    id = Column(GUID, primary_key=True, default=GUID.default_value)

    url = Column(String(200), nullable=False, unique=True)
    backend = Column(Enum(RepositoryBackend), default=RepositoryBackend.unknown, nullable=False)
    status = Column(Enum(RepositoryStatus), default=RepositoryStatus.inactive, nullable=False)
    data = Column(JSONEncodedDict)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_update = Column(DateTime)
    last_update_attempt = Column(DateTime)

    query_class = RepositoryAccessBoundQuery

    __tablename__ = 'repository'

    def get_vcs(self):
        from zeus.models import ItemOption
        from zeus.vcs.git import GitVcs

        options = dict(
            db.session.query(ItemOption.name, ItemOption.value).filter(
                ItemOption.item_id == self.id, ItemOption.name.in_([
                    'auth.username',
                ])))

        kwargs = {
            'path': os.path.join(current_app.config['REPO_ROOT'], self.id.hex),
            'url': self.url,
            'username': options.get('auth.username'),
        }

        if self.backend == RepositoryBackend.git:
            return GitVcs(**kwargs)
        else:
            raise NotImplementedError('Invalid backend: {}'.format(self.backend))
