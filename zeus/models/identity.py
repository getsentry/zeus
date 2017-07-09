from datetime import datetime

from zeus.config import db
from zeus.db.types import GUID, JSONEncodedDict
from zeus.db.utils import model_repr


class Identity(db.Model):
    """
    Identities associated with a user. Primarily used for Single Sign-On.
    """
    id = db.Column(GUID, primary_key=True, default=GUID.default_value)
    user_id = db.Column(
        GUID, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False, index=True
    )
    external_id = db.Column(db.String(64), unique=True, nullable=False)
    provider = db.Column(db.String(32), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    config = db.Column(JSONEncodedDict)

    user = db.relationship('User')

    __tablename__ = 'identity'
    __table_args__ = (db.UniqueConstraint('user_id', 'provider', name='unq_identity_user'), )
    __repr__ = model_repr('user_id', 'provider', 'external_id')
