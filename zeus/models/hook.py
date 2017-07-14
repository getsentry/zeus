import hmac

from hashlib import sha256
from secrets import compare_digest, token_bytes

from zeus.config import db
from zeus.db.mixins import ProjectBoundMixin, StandardAttributes
from zeus.db.utils import model_repr


class Hook(ProjectBoundMixin, StandardAttributes, db.Model):
    """
    An webhook bound to a single respository.
    """
    token = db.Column(
        db.LargeBinary(64), default=lambda: Hook.generate_token(), unique=True, nullable=False
    )
    provider = db.Column(db.String(64), nullable=False)

    project = db.relationship('Project')

    __tablename__ = 'hook'
    __repr__ = model_repr('project_id')

    @classmethod
    def generate_token(cls):
        return token_bytes(64)

    def get_signature(self):
        return hmac.new(key=self.token, msg=self.project_id.bytes, digestmod=sha256).hexdigest()

    def is_valid_signature(self, signature):
        return compare_digest(self.get_signature(), signature)
