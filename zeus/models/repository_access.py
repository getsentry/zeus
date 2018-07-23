from zeus.config import db
from zeus.constants import Permission
from zeus.db.mixins import RepositoryMixin
from zeus.db.types import Enum, GUID
from zeus.db.utils import model_repr


class RepositoryAccess(RepositoryMixin, db.Model):
    user_id = db.Column(
        GUID, db.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    permission = db.Column(
        Enum(Permission), nullable=False, default=Permission.read, server_default="1"
    )

    user = db.relationship("User", innerjoin=True, uselist=False)

    __tablename__ = "repository_access"
    __repr__ = model_repr("repository_id", "user_id")
