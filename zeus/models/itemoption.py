from datetime import datetime
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.schema import UniqueConstraint

from zeus.config import db
from zeus.db.types import GUID


class ItemOption(db.Model):
    id = Column(GUID, primary_key=True, default=GUID.default_value)
    item_id = Column(GUID, nullable=False)
    name = Column(String(64), nullable=False)
    value = Column(Text, nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)

    __tablename__ = 'itemoption'
    __table_args__ = (
        UniqueConstraint('item_id', 'name', name='unq_itemoption_name'),
    )
