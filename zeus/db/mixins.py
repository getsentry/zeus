import sqlalchemy

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
class BoundQuery(db.Query):
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

    def unrestricted_unsafe(self):
        rv = self._clone()
        rv.current_constrained = False
        return rv

    def constrained(self):
        if not self.current_constrained:
            return self

        mzero = self._mapper_zero()
        if mzero is not None:
            constraints = self.get_constraints(mzero)
            return self.enable_assertions(False).filter(constraints)
        return self


class OrganizationBoundQuery(BoundQuery):
    def get_constraints(self, mzero):
        from zeus.auth import get_current_tenant

        tenant = get_current_tenant()
        if tenant.organization_ids:
            return mzero.class_.organization_id.in_(tenant.organization_ids)
        return sqlalchemy.sql.false()


class ProjectBoundQuery(BoundQuery):
    def get_constraints(self, mzero):
        from zeus.auth import get_current_tenant

        tenant = get_current_tenant()
        if tenant.project_ids:
            return mzero.class_.project_id.in_(tenant.project_ids)
        return sqlalchemy.sql.false()


class RepositoryBoundQuery(BoundQuery):
    def get_constraints(self, mzero):
        from zeus.auth import get_current_tenant

        tenant = get_current_tenant()
        if tenant.project_ids:
            return mzero.class_.repository_id.in_(tenant.repository_ids)
        return sqlalchemy.sql.false()


class OrganizationBoundMixin(object):
    query_class = OrganizationBoundQuery

    @declared_attr
    def organization_id(cls):
        return db.Column(
            GUID, db.ForeignKey('organization.id', ondelete='CASCADE'), nullable=False, index=True
        )

    @declared_attr
    def organization(cls):
        return db.relationship('Organization', innerjoin=True, uselist=False)


class ProjectBoundMixin(OrganizationBoundMixin):
    query_class = ProjectBoundQuery

    @declared_attr
    def project_id(cls):
        return db.Column(
            GUID, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False, index=True
        )

    @declared_attr
    def project(cls):
        return db.relationship('Project', innerjoin=True, uselist=False)


class RepositoryBoundMixin(OrganizationBoundMixin):
    query_class = RepositoryBoundQuery

    @declared_attr
    def repository_id(cls):
        return db.Column(
            GUID, db.ForeignKey('repository.id', ondelete='CASCADE'), nullable=False, index=True
        )

    @declared_attr
    def repository(cls):
        return db.relationship('Repository', innerjoin=True, uselist=False)
