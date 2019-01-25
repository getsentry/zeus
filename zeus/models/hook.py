import hmac

from hashlib import sha256
from secrets import compare_digest, token_bytes
from typing import List

from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.utils import model_repr
from zeus.db.types import JSONEncodedDict


class Hook(RepositoryBoundMixin, StandardAttributes, db.Model):
    """
    An webhook bound to a single respository.
    """

    token = db.Column(
        db.LargeBinary(64),
        default=lambda: Hook.generate_token(),
        unique=True,
        nullable=False,
    )
    provider = db.Column(db.String(64), nullable=False)
    is_required = db.Column(db.Boolean, nullable=True)
    # the provider controls the format of data
    config = db.Column(JSONEncodedDict, nullable=True)

    __tablename__ = "hook"
    __repr__ = model_repr("repository_id", "provider")

    @classmethod
    def generate_token(cls) -> bytes:
        return token_bytes(64)

    def get_signature(self) -> bytes:
        return hmac.new(
            key=self.token, msg=self.repository_id.bytes, digestmod=sha256
        ).hexdigest()

    def is_valid_signature(self, signature: bytes) -> bool:
        return compare_digest(self.get_signature(), signature)

    def get_provider(self):
        from zeus.providers import get_provider

        return get_provider(self.provider)

    @classmethod
    def get_required_hook_ids(cls, repository_id: str) -> List[str]:
        return sorted(
            [
                str(h)
                for h, in db.session.query(Hook.id).filter(
                    Hook.repository_id == repository_id,
                    Hook.is_required == True,  # NOQA
                )
            ]
        )
