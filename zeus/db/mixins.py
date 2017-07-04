import sqlalchemy

from sqlalchemy.ext.declarative import declared_attr

from zeus.auth import get_current_tenant
from zeus.db.types import GUID
from zeus.config import db


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
        if not self.current_constrained:
            return self

        mzero = self._mapper_zero()
        if mzero is not None:
            tenant = get_current_tenant()
            if tenant.repository_ids:
                return self.enable_assertions(False).filter(
                    mzero.class_.repository_id.in_(
                        tenant.repository_ids)
                )
            else:
                return self.enable_assertions(False).filter(sqlalchemy.sql.false())
        return self

    def unconstrained_unsafe(self):
        rv = self._clone()
        rv.current_constrained = False
        return rv

# class RepositoryQuery(db.Query):
#     current_tenant_constrained = True

#     def tenant_unconstrained_unsafe(self):
#         rv = self._clone()
#         rv.current_tenant_constrained = False
#         return rv


# @db.event.listens_for(RepositoryQuery, 'before_compile', retval=True)
# def ensure_tenant_constrainted(query: db.Query) -> db.Query:
#     if not query.current_tenant_constrained:
#         return query
#     for desc in query.column_descriptions:
#         # should we just hard error if we dont find the column?
#         if hasattr(desc['type'], 'repository_id'):
#             tenant = get_current_tenant()
#             if tenant.repository_ids:
#                 query = query.filter(
#                     query._mapper_zero().class_.repository_id.in_(
#                         tenant.repository_ids)
#                 )
#             else:
#                 query = query.filter(sqlalchemy.sql.false())
#     return query


class RepositoryBoundMixin(object):
    query_class = RepositoryBoundQuery

    @declared_attr
    def repository_id(cls):
        return db.Column(GUID, db.ForeignKey(
            'repository.id', ondelete='CASCADE'), nullable=False, index=True)

    @declared_attr
    def repository(cls):
        return db.relationship('Repository', innerjoin=True, uselist=False)
