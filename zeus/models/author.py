from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin
from zeus.db.types import GUID
from zeus.db.utils import model_repr


class Author(RepositoryBoundMixin, db.Model):
    """
    The author of a source. Generally used for things like commit authors.

    This is different than User, which indicates a known authenticatable user.
    """

    id = db.Column(GUID, primary_key=True, default=GUID.default_value)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=True)

    __tablename__ = "author"
    __table_args__ = (
        db.UniqueConstraint("repository_id", "email", name="unq_author_email"),
    )
    __repr__ = model_repr("repository_id", "name", "email")
