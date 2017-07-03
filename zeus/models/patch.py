from __future__ import absolute_import

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from zeus.config import db
from zeus.db.types import GUID


class Patch(db.Model):
    id = Column(GUID, primary_key=True, default=GUID.default_value)
    repository_id = Column(GUID, ForeignKey(
        'repository.id', ondelete="CASCADE"), nullable=False)
    parent_revision_sha = Column(String(40), nullable=False)
    diff = Column(Text, nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)

    repository = relationship('Repository')

    __tablename__ = 'patch'

    __table_args__ = (
        Index('idx_repo_sha', 'repository_id', 'parent_revision_sha'),
    )
