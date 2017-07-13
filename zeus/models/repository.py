import enum
import os.path
import sqlalchemy

from flask import current_app
from sqlalchemy import event
from sqlalchemy.sql import func
from urllib.parse import urlparse

from zeus.config import db
from zeus.db.types import Enum, GUID, JSONEncodedDict
from zeus.db.utils import model_repr
from zeus.utils.text import slugify
from zeus.utils import timezone


class RepositoryBackend(enum.Enum):
    unknown = 0
    git = 1

    def __str__(self):
        return self.name


class RepositoryStatus(enum.Enum):
    inactive = 0
    active = 1
    importing = 2

    def __str__(self):
        return self.name


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
                return self.enable_assertions(False
                                              ).filter(mzero.class_.id.in_(tenant.repository_ids))
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
    id = db.Column(GUID, primary_key=True, default=GUID.default_value)

    name = db.Column(db.String(200), nullable=False, unique=True)
    url = db.Column(db.String(200), nullable=False, unique=True)
    backend = db.Column(Enum(RepositoryBackend), default=RepositoryBackend.unknown, nullable=False)
    status = db.Column(Enum(RepositoryStatus), default=RepositoryStatus.inactive, nullable=False)
    data = db.Column(JSONEncodedDict, nullable=True)
    date_created = db.Column(
        db.TIMESTAMP(timezone=True),
        default=timezone.now,
        server_default=func.now(),
        nullable=False
    )
    last_update = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    last_update_attempt = db.Column(db.TIMESTAMP(timezone=True), nullable=True)

    options = db.relationship(
        'ItemOption',
        foreign_keys='[ItemOption.item_id]',
        primaryjoin='ItemOption.item_id == Repository.id',
        lazy='subquery',
        viewonly=True,
        uselist=True
    )

    query_class = RepositoryAccessBoundQuery

    __tablename__ = 'repository'
    __repr__ = model_repr('name', 'url')

    def get_vcs(self):
        from zeus.models import ItemOption
        from zeus.vcs.git import GitVcs

        options = dict(
            db.session.query(ItemOption.name, ItemOption.value)
            .filter(ItemOption.item_id == self.id, ItemOption.name.in_([
                'auth.username',
            ]))
        )

        kwargs = {
            'path': os.path.join(current_app.config['REPO_ROOT'], self.id.hex),
            'url': self.url,
            'username': options.get('auth.username'),
        }

        if self.backend == RepositoryBackend.git:
            return GitVcs(**kwargs)
        else:
            raise NotImplementedError('Invalid backend: {}'.format(self.backend))


@event.listens_for(Repository.url, 'set', retval=False)
def set_name(target, value, oldvalue, initiator):
    if value and not target.name:
        parts = urlparse(value)
        target.name = slugify(parts.path.split('.git', 1)[0][1:])
    return value
