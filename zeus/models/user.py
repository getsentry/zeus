from sqlalchemy import func

from zeus.config import db
from zeus.db.mixins import StandardAttributes
from zeus.db.utils import model_repr
from zeus.utils import timezone


class User(StandardAttributes, db.Model):
    """
    Actors within Zeus.
    """

    email = db.Column(db.String(128), unique=True, nullable=False)
    date_active = db.Column(
        db.TIMESTAMP(timezone=True),
        nullable=False,
        default=timezone.now,
        server_default=func.now(),
        index=True,
    )

    options = db.relationship(
        "ItemOption",
        foreign_keys="[ItemOption.item_id]",
        primaryjoin="ItemOption.item_id == User.id",
        viewonly=True,
        uselist=True,
    )

    __tablename__ = "user"
    __repr__ = model_repr("email")
