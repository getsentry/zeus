from datetime import datetime

from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin
from zeus.db.types import GUID


class Patch(RepositoryBoundMixin, db.Model):
    id = db.Column(GUID, primary_key=True, default=GUID.default_value)
    parent_revision_sha = db.Column(db.String(40), nullable=False)
    diff = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __tablename__ = 'patch'

    __table_args__ = (db.Index('idx_repo_sha', 'repository_id', 'parent_revision_sha'), )
