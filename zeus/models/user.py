from zeus.config import db
from zeus.db.mixins import StandardAttributes
from zeus.db.utils import model_repr


class User(StandardAttributes, db.Model):
    """
    Actors within Zeus.
    """

    email = db.Column(db.String(128), unique=True, nullable=False)

    options = db.relationship(
        "ItemOption",
        foreign_keys="[ItemOption.item_id]",
        primaryjoin="ItemOption.item_id == User.id",
        viewonly=True,
        uselist=True,
    )

    __tablename__ = "user"
    __repr__ = model_repr("email")
