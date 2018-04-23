from zeus.config import db
from zeus.db.types import GUID
from zeus.db.utils import model_repr


class ItemSequence(db.Model):
    parent_id = db.Column(GUID, nullable=False, primary_key=True)
    value = db.Column(
        db.Integer, default=0, server_default="0", nullable=False, primary_key=True
    )

    __tablename__ = "itemsequence"
    __repr__ = model_repr("parent_id", "value")
