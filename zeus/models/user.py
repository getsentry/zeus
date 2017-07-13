from sqlalchemy.sql import func

from zeus.config import db
from zeus.db.types.guid import GUID
from zeus.db.utils import model_repr
from zeus.utils import timezone


class User(db.Model):
    """
    Actors within Zeus.
    """
    id = db.Column(GUID, primary_key=True, default=GUID.default_value)
    email = db.Column(db.String(128), unique=True, nullable=False)
    date_created = db.Column(
        db.TIMESTAMP(timezone=True),
        default=timezone.now,
        server_default=func.now(),
        nullable=False
    )

    __tablename__ = 'user'
    __repr__ = model_repr('email')
