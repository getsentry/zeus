from datetime import datetime

from zeus.config import db

from sqlalchemy import Column, DateTime

from .types import GUID


class ModelMixin(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(GUID, primary_key=True, default=GUID.default_value)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, *args, **kwargs):
        self.id = GUID.default_value()
        self.date_created = datetime.utcnow()
        super(BaseModel, self).__init__(*args, **kwargs)
