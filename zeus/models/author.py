from datetime import datetime

from zeus.config import db
from zeus.db.types import GUID


class Author(db.Model):
    """
    The author of a source. Generally used for things like commit authors.

    This is different than User, which indicates a known authenticatable user.
    """
    id = db.Column(GUID, primary_key=True, default=GUID.default_value)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=True, unique=True)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    __tablename__ = 'author'
