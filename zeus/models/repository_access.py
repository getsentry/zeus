from zeus.config import db
from zeus.db.mixins import OrganizationBoundMixin
from zeus.db.types import GUID
from zeus.db.utils import model_repr


class RepositoryAccess(OrganizationBoundMixin, db.Model):
    repository_id = db.Column(GUID, db.ForeignKey('repository.id'), primary_key=True)
    user_id = db.Column(GUID, db.ForeignKey('user.id'), primary_key=True)

    repository = db.relationship('Repository', innerjoin=True, uselist=False)
    user = db.relationship('User', innerjoin=True, uselist=False)

    __tablename__ = 'repository_access'
    __repr__ = model_repr('repository_id', 'user_id')
