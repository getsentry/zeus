from zeus.config import db
from zeus.constants import Permission
from zeus.db.types import Enum, GUID
from zeus.db.utils import model_repr


class ApiTokenRepositoryAccess(db.Model):
    repository_id = db.Column(GUID, db.ForeignKey("repository.id"), primary_key=True)
    api_token_id = db.Column(GUID, db.ForeignKey("api_token.id"), primary_key=True)
    permission = db.Column(Enum(Permission), nullable=False, default=Permission.read)

    repository = db.relationship("Repository", innerjoin=True, uselist=False)
    api_token = db.relationship("ApiToken", innerjoin=True, uselist=False)

    __tablename__ = "api_token_repository_access"
    __repr__ = model_repr("repository_id", "api_token_id")
