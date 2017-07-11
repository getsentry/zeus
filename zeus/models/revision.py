from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY

from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin
from zeus.db.types import GUID
from zeus.db.utils import model_repr


class Revision(RepositoryBoundMixin, db.Model):
    sha = db.Column(db.String(40), primary_key=True)
    author_id = db.Column(GUID, db.ForeignKey('author.id'), index=True, nullable=True)
    committer_id = db.Column(GUID, db.ForeignKey('author.id'), index=True, nullable=True)
    message = db.Column(db.Text, nullable=True)
    parents = db.Column(ARRAY(db.String(40)), nullable=True)
    branches = db.Column(ARRAY(db.String(128)), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    date_committed = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    author = db.relationship('Author', foreign_keys=[author_id])
    committer = db.relationship('Author', foreign_keys=[committer_id])

    __tablename__ = 'revision'
    __table_args__ = (db.UniqueConstraint(
        'repository_id',
        'sha',
        name='unq_revision',
    ), )
    __repr__ = model_repr('repository_id', 'sha', 'subject')

    @property
    def subject(self):
        return self.message.splitlines()[0]
