from datetime import timedelta
from secrets import token_hex

from zeus.config import db
from zeus.db.mixins import StandardAttributes
from zeus.db.utils import model_repr
from zeus.utils import timezone

DEFAULT_EXPIRATION = timedelta(days=30)


class ApiToken(StandardAttributes, db.Model):
    """
    An API token.
    """

    access_token = db.Column(
        db.String(64),
        default=lambda: ApiToken.generate_token(),
        unique=True,
        nullable=False,
    )
    refresh_token = db.Column(
        db.String(64),
        default=lambda: ApiToken.generate_token(),
        unique=True,
        nullable=False,
    )
    expires_at = db.Column(
        db.TIMESTAMP(timezone=True),
        nullable=True,
        default=lambda: timezone.now() + DEFAULT_EXPIRATION,
    )

    __tablename__ = "api_token"
    __repr__ = model_repr("id")

    @classmethod
    def generate_token(cls):
        return token_hex(32)

    def is_expired(self):
        if not self.expires_at:
            return False

        return timezone.now() >= self.expires_at

    def refresh(self, expires_at=None):
        if expires_at is None:
            expires_at = timezone.now() + DEFAULT_EXPIRATION

        with db.session.begin_nested():
            self.token = type(self).generate_token()
            self.refresh_token = type(self).generate_token()
            self.expires_at = expires_at
            db.session.add(self)
            db.session.commit()
