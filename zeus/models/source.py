from __future__ import absolute_import

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index, ForeignKeyConstraint, UniqueConstraint

from zeus.config import db
from zeus.db.types import GUID, JSONEncodedDict


class Source(db.Model):
    """
    A source represents the canonical parameters that a build is running against.
    """
    id = Column(GUID, primary_key=True, default=GUID.default_value)
    repository_id = Column(GUID, ForeignKey('repository.id'), nullable=False)
    patch_id = Column(GUID, ForeignKey('patch.id'), unique=True, nullable=True)
    revision_sha = Column(String(40), nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    data = Column(JSONEncodedDict)

    repository = relationship('Repository', innerjoin=False)
    patch = relationship('Patch')
    revision = relationship('Revision',
                            foreign_keys=[repository_id, revision_sha], viewonly=True)

    __tablename__ = 'source'
    __table_args__ = (
        ForeignKeyConstraint(
            ('repository_id', 'revision_sha'),
            ('revision.repository_id', 'revision.sha')
        ),
        Index('idx_source_repo_sha', 'repository_id', 'revision_sha'),
        Index('idx_source_patch', 'patch_id'),
        UniqueConstraint(
            'repository_id', 'revision_sha', 'patch_id', name='unq_source_revision',
        ),
    )

    def is_commit(self):
        return self.patch_id is None and self.revision_sha
