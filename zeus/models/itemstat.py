from zeus.config import db
from zeus.db.types import GUID


class ItemStat(db.Model):
    id = db.Column(GUID, primary_key=True, default=GUID.default_value)
    item_id = db.Column(GUID, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    value = db.Column(db.Integer, nullable=False)

    __tablename__ = 'itemstat'
    __table_args__ = (db.UniqueConstraint('item_id', 'name', name='unq_itemstat_name'), )
