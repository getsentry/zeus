from zeus.config import db
from zeus.db.mixins import StandardAttributes
from zeus.db.types import GUID
from zeus.db.utils import model_repr


class Email(StandardAttributes, db.Model):
    """
    An email address associated with a user.
    """
    user_id = db.Column(
        GUID, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False, index=True
    )
    email = db.Column(db.String(128), nullable=False)
    verified = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship('User')

    __tablename__ = 'email'
    __table_args__ = (db.UniqueConstraint(
        'user_id', 'email', name='unq_user_email'), )
    __repr__ = model_repr('user_id', 'email', 'verified')
