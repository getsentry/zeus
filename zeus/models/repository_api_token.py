from zeus.config import db
from zeus.db.mixins import ApiTokenMixin, RepositoryMixin, StandardAttributes
from zeus.db.utils import model_repr


class RepositoryApiToken(StandardAttributes, RepositoryMixin, ApiTokenMixin, db.Model):
    """
    An API token associated to a repository.
    """

    __tablename__ = "repository_api_token"
    __repr__ = model_repr("repository_id", "key")

    def get_token_key(self):
        return "r"
