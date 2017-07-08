from zeus.config import db
from zeus.db.types import GUID


class RepositoryAccess(db.Model):
    repository_id = db.Column(GUID, db.ForeignKey('repository.id'), primary_key=True)
    user_id = db.Column(GUID, db.ForeignKey('user.id'), primary_key=True)

    repository = db.relationship('Repository', innerjoin=True, uselist=False)
    user = db.relationship('User', innerjoin=True, uselist=False)

    __tablename__ = 'repository_access'
