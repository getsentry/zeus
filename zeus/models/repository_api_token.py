from zeus.config import db
from zeus.db.mixins import ApiTokenMixin, StandardAttributes
from zeus.db.types import GUID
from zeus.db.utils import model_repr


class RepositoryApiToken(StandardAttributes, db.Model, ApiTokenMixin):
    """
    An API token associated to users.
    """

    repository_id = db.Column(
        GUID,
        db.ForeignKey("repository.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    repository = db.relationship(
        "Repository", backref=db.backref("token", uselist=False), innerjoin=True
    )

    __tablename__ = "repository_api_token"
    __repr__ = model_repr("repository_id", "key")

    def get_token_key(self):
        return "r"

    def get_tenant(self):
        return self.user
