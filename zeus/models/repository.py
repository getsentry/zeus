import enum
import os.path

from flask import current_app
from sqlalchemy import or_

from zeus.config import db
from zeus.db.mixins import StandardAttributes
from zeus.db.types import Enum, StrEnum, JSONEncodedDict
from zeus.db.utils import model_repr


class RepositoryBackend(enum.IntEnum):
    unknown = 0
    git = 1

    def __str__(self):
        return self.name


class RepositoryProvider(enum.Enum):
    github = 'gh'

    def __str__(self):
        return self.value


class RepositoryStatus(enum.IntEnum):
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
            cls = mzero.class_
            tenant = get_current_tenant()
            if tenant.repository_ids:
                return self.enable_assertions(False).filter(or_(
                    cls.id.in_(tenant.repository_ids),
                    cls.public == True  # NOQA
                ))
            else:
                return self.enable_assertions(False).filter(
                    cls.public == True,  # NOQA
                )
        return self

    def unrestricted_unsafe(self):
        rv = self._clone()
        rv.current_constrained = False
        return rv


class Repository(StandardAttributes, db.Model):
    """
    Represents a single repository.
    """
    # TODO(dcramer): we dont want to be coupled to GitHub (the concept of orgs)
    # but right now we simply dont care, and this can be refactored later (URLs
    # are tricky)
    owner_name = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    backend = db.Column(Enum(RepositoryBackend),
                        default=RepositoryBackend.unknown, nullable=False)
    status = db.Column(Enum(RepositoryStatus),
                       default=RepositoryStatus.inactive, nullable=False)
    provider = db.Column(StrEnum(RepositoryProvider), nullable=False)
    external_id = db.Column(db.String(64))
    data = db.Column(JSONEncodedDict, nullable=True)
    public = db.Column(db.Boolean, default=False, nullable=False)
    last_update = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    last_update_attempt = db.Column(db.TIMESTAMP(timezone=True), nullable=True)

    options = db.relationship(
        'ItemOption',
        foreign_keys='[ItemOption.item_id]',
        primaryjoin='ItemOption.item_id == Repository.id',
        viewonly=True,
        uselist=True
    )

    query_class = RepositoryAccessBoundQuery

    __tablename__ = 'repository'
    __table_args__ = (
        db.UniqueConstraint('provider', 'external_id',
                            name='unq_repo_external_id'),
        db.UniqueConstraint('provider', 'owner_name',
                            'name', name='unq_repo_name'),
    )
    __repr__ = model_repr('name', 'url', 'provider')

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
            'id': self.id.hex,
            'url': self.url,
            'username': options.get('auth.username'),
        }

        if self.backend == RepositoryBackend.git:
            return GitVcs(**kwargs)
        else:
            raise NotImplementedError(
                'Invalid backend: {}'.format(self.backend))

    def get_full_name(self):
        return '{}/{}/{}'.format(self.provider, self.owner_name, self.name)
