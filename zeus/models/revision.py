from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from zeus.config import db
from zeus.db.types import GUID


class Revision(db.Model):
    repository_id = Column(GUID, ForeignKey('repository.id'), primary_key=True)
    sha = Column(String(40), primary_key=True)
    author_id = Column(GUID, ForeignKey('author.id'))
    committer_id = Column(GUID, ForeignKey('author.id'))
    message = Column(Text)
    parents = Column(ARRAY(String(40)))
    branches = Column(ARRAY(String(128)))
    date_created = Column(DateTime, default=datetime.utcnow)
    date_committed = Column(DateTime, default=datetime.utcnow)

    repository = relationship('Repository')
    author = relationship('Author', foreign_keys=[author_id], innerjoin=False)
    committer = relationship('Author', foreign_keys=[
                             committer_id], innerjoin=False)

    __tablename__ = 'revision'
    __table_args__ = (
        Index('idx_revision_author', 'author_id'),
        Index('idx_revision_committer', 'committer_id'),
    )

    @property
    def subject(self):
        return self.message.splitlines()[0]
