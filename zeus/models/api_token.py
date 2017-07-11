from datetime import datetime, timedelta
from uuid import uuid4

from zeus.config import db
from zeus.db.types import GUID
from zeus.db.utils import model_repr

DEFAULT_EXPIRATION = timedelta(days=30)


class ApiToken(db.Model):
    """
    An API token.
    """
    id = db.Column(GUID, primary_key=True, default=GUID.default_value)
    access_token = db.Column(
        db.String(64), default=lambda: ApiToken.generate_token(), unique=True, nullable=False
    )
    refresh_token = db.Column(
        db.String(64), default=lambda: ApiToken.generate_token(), unique=True, nullable=False
    )
    expires_at = db.Column(
        db.DateTime, nullable=True, default=lambda: datetime.utcnow() + DEFAULT_EXPIRATION
    )
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    __tablename__ = 'api_token'
    __repr__ = model_repr('id')

    @classmethod
    def generate_token(cls):
        return uuid4().hex + uuid4().hex

    def is_expired(self):
        if not self.expires_at:
            return False

        return datetime.utcnow() >= self.expires_at

    def refresh(self, expires_at=None):
        if expires_at is None:
            expires_at = datetime.utcnow() + DEFAULT_EXPIRATION

        with db.session.begin_nested():
            self.token = type(self).generate_token()
            self.refresh_token = type(self).generate_token()
            self.expires_at = expires_at
            db.session.add(self)
            db.session.commit()
