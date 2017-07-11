from datetime import datetime

from zeus.config import db
from zeus.db.types.guid import GUID
from zeus.db.utils import model_repr


class User(db.Model):
    """
    Actors within Zeus.
    """
    id = db.Column(GUID, primary_key=True, default=GUID.default_value)
    email = db.Column(db.String(128), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __tablename__ = 'user'
    __repr__ = model_repr('email')
