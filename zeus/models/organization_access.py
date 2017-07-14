from zeus.config import db
from zeus.db.types import GUID
from zeus.db.utils import model_repr


class OrganizationAccess(db.Model):
    organization_id = db.Column(GUID, db.ForeignKey('organization.id'), primary_key=True)
    user_id = db.Column(GUID, db.ForeignKey('user.id'), primary_key=True)

    organization = db.relationship('Organization', innerjoin=True, uselist=False)
    user = db.relationship('User', innerjoin=True, uselist=False)

    __tablename__ = 'organization_access'
    __repr__ = model_repr('organization_id', 'user_id')
