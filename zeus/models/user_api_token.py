from zeus.config import db
from zeus.db.mixins import ApiTokenMixin, StandardAttributes
from zeus.db.types import GUID
from zeus.db.utils import model_repr


class UserApiToken(StandardAttributes, db.Model, ApiTokenMixin):
    """
    An API token associated to users.
    """

    user_id = db.Column(
        GUID, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    user = db.relationship(
        "User", backref=db.backref("tokens", uselist=False), innerjoin=True
    )

    __tablename__ = "user_api_token"
    __repr__ = model_repr("user_id", "key")

    def get_token_key(self):
        return "u"
