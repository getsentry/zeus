from datetime import datetime
from sqlalchemy import Column, String, DateTime

from zeus.config import db
from zeus.db.types import GUID


class Author(db.Model):
    """
    The author of a source. Generally used for things like commit authors.

    This is different than User, which indicates a known authenticatable user.
    """
    id = Column(GUID, primary_key=True, default=GUID.default_value)
    name = Column(String(128), nullable=False)
    email = Column(String(128), nullable=True, unique=True)
    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)

    __tablename__ = 'author'
