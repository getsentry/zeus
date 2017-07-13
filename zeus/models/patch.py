from sqlalchemy.sql import func

from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin
from zeus.db.types import GUID
from zeus.db.utils import model_repr
from zeus.utils import timezone


class Patch(RepositoryBoundMixin, db.Model):
    id = db.Column(GUID, primary_key=True, default=GUID.default_value)
    parent_revision_sha = db.Column(db.String(40), nullable=False)
    diff = db.deferred(db.Column(db.Text, nullable=False))
    date_created = db.Column(
        db.TIMESTAMP(timezone=True),
        default=timezone.now,
        server_default=func.now(),
        nullable=False
    )

    parent_revision = db.relationship(
        'Revision', foreign_keys='[Patch.repository_id, Patch.parent_revision_sha]', viewonly=True
    )

    __tablename__ = 'patch'
    __table_args__ = (
        db.ForeignKeyConstraint(
            ('repository_id', 'parent_revision_sha'), ('revision.repository_id', 'revision.sha')
        ), db.Index('idx_repo_sha', 'repository_id', 'parent_revision_sha'),
    )
    __repr__ = model_repr('repository_id', 'parent_revision_sha')
