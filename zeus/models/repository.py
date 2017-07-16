import enum
import os.path
import sqlalchemy

from flask import current_app
from sqlalchemy import event

from zeus.config import db
from zeus.db.mixins import BoundQuery, OrganizationBoundMixin, StandardAttributes
from zeus.db.types import Enum, StrEnum, JSONEncodedDict
from zeus.db.utils import model_repr


class RepositoryBackend(enum.Enum):
    unknown = 0
    git = 1

    def __str__(self):
        return self.name


class RepositoryProvider(enum.Enum):
    native = 'native'
    github = 'github'

    def __str__(self):
        return self.name


class RepositoryStatus(enum.Enum):
    inactive = 0
    active = 1
    importing = 2

    def __str__(self):
        return self.name


class RepositoryAccessBoundQuery(BoundQuery):
    def get_constraints(self, mzero):
        from zeus import auth
        tenant = auth.get_current_tenant()
        if tenant.repository_ids:
            return mzero.class_.id.in_(tenant.repository_ids)
        return sqlalchemy.sql.false()


class Repository(OrganizationBoundMixin, StandardAttributes, db.Model):
    """
    Represents a single repository.
    """
    query_class = RepositoryAccessBoundQuery

    provider = db.Column(
        StrEnum(RepositoryProvider), default=RepositoryProvider.native, nullable=False
    )
    external_id = db.Column(db.String(64))
    url = db.Column(db.String(200), nullable=False)
    backend = db.Column(Enum(RepositoryBackend), default=RepositoryBackend.unknown, nullable=False)
    status = db.Column(Enum(RepositoryStatus), default=RepositoryStatus.inactive, nullable=False)
    data = db.Column(JSONEncodedDict, nullable=True)
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

    __tablename__ = 'repository'
    __table_args__ = (
        db.UniqueConstraint('organization_id', 'provider', 'external_id', name='unq_external_id'),
    )
    __repr__ = model_repr('url', 'provider', 'external_id')

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


@event.listens_for(Repository.provider, 'set', retval=False)
def set_native_external_id(target, value, oldvalue, initiator):
    if not value:
        return value

    if value == RepositoryProvider.native:
        target.external_id = target.url
    return value


@event.listens_for(Repository.url, 'set', retval=False)
def set_native_external_id(target, value, oldvalue, initiator):
    if not value:
        return value

    if target.provider == RepositoryProvider.native:
        target.external_id = value
    return value
