from datetime import datetime
from sqlalchemy import Column, String, DateTime

from zeus.config import db
from zeus.db.types.guid import GUID


class User(db.Model):
    """
    Actors within Zeus.
    """
    id = Column(GUID, primary_key=True, default=GUID.default_value)
    email = Column(String(128), unique=True, nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)

    __tablename__ = 'user'
