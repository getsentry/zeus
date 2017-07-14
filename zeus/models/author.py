from zeus.config import db
from zeus.db.mixins import OrganizationBoundMixin
from zeus.db.types import GUID
from zeus.db.utils import model_repr


class Author(OrganizationBoundMixin, db.Model):
    """
    The author of a source. Generally used for things like commit authors.

    This is different than User, which indicates a known authenticatable user.
    """
    id = db.Column(GUID, primary_key=True, default=GUID.default_value)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=True)

    __tablename__ = 'author'
    __table_args__ = (db.UniqueConstraint('organization_id', 'email', name='unq_author_email'), )
    __repr__ = model_repr('organization_id', 'name', 'email')
