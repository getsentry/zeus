import sqlalchemy

from zeus.config import db
from zeus.db.mixins import BoundQuery, StandardAttributes
from zeus.db.utils import model_repr


class OrganizationAccessBoundQuery(BoundQuery):
    def get_constraints(self, mzero):
        from zeus import auth

        tenant = auth.get_current_tenant()
        if tenant.organization_ids:
            return mzero.class_.id.in_(tenant.organization_ids)
        return sqlalchemy.sql.false()


class Organization(StandardAttributes, db.Model):
    """
    Represents a single organization.
    """
    name = db.Column(db.String(200), nullable=False, unique=True)

    query_class = OrganizationAccessBoundQuery

    __tablename__ = 'organization'
    __repr__ = model_repr('name')
