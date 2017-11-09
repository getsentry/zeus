import sqlalchemy

from secrets import token_hex
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func

from zeus.db.types import GUID
from zeus.config import db
from zeus.utils import timezone


class StandardAttributes(object):
    @declared_attr
    def id(cls):
        return db.Column(GUID, primary_key=True, default=GUID.default_value)

    @declared_attr
    def date_created(cls):
        return db.Column(
            db.TIMESTAMP(timezone=True),
            default=timezone.now,
            server_default=func.now(),
            nullable=False
        )


# https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/PreFilteredQuery
class RepositoryBoundQuery(db.Query):
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
                    mzero.class_.repository_id.in_(tenant.repository_ids)
                )
            else:
                return self.enable_assertions(False).filter(sqlalchemy.sql.false())
        return self

    def unrestricted_unsafe(self):
        rv = self._clone()
        rv.current_constrained = False
        return rv


class RepositoryBoundMixin(object):
    query_class = RepositoryBoundQuery

    @declared_attr
    def repository_id(cls):
        return db.Column(
            GUID, db.ForeignKey('repository.id', ondelete='CASCADE'), nullable=False, index=True
        )

    @declared_attr
    def repository(cls):
        return db.relationship('Repository', innerjoin=True, uselist=False)


class ApiTokenMixin(object):
    @declared_attr
    def key(cls):
        return db.Column(
            db.String(64), default=lambda: ApiTokenMixin.generate_token(), unique=True, nullable=False
        )

    @classmethod
    def generate_token(cls):
        return token_hex(32)

    def get_token_key(self):
        raise NotImplementedError

    def get_tenant(self):
        raise NotImplementedError
