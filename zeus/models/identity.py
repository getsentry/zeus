from datetime import datetime
from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

from zeus.config import db
from zeus.db.types import GUID, JSONEncodedDict


class Identity(db.Model):
    """
    Identities associated with a user. Primarily used for Single Sign-On.
    """
    __tablename__ = 'identity'
    __table_args__ = (
        UniqueConstraint('user_id', 'provider', name='unq_identity_user'),
    )

    id = Column(GUID, primary_key=True, default=GUID.default_value)
    user_id = Column(GUID, ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    external_id = Column(String(64), unique=True, nullable=False)
    provider = Column(String(32), nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    config = Column(JSONEncodedDict)

    user = relationship('User')
