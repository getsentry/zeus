from datetime import datetime

from zeus.config import db
from zeus.db.types.guid import GUID


class User(db.Model):
    """
    Actors within Zeus.
    """
    id = db.Column(GUID, primary_key=True, default=GUID.default_value)
    email = db.Column(db.String(128), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    __tablename__ = 'user'
