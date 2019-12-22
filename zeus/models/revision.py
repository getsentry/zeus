
from flask import current_app
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func

from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin
from zeus.db.types import GUID
from zeus.db.utils import model_repr
from zeus.exceptions import UnknownRepositoryBackend
from zeus.utils import timezone


class Revision(RepositoryBoundMixin, db.Model):
    sha = db.Column(db.String(40), primary_key=True)
    author_id = db.Column(
        GUID, db.ForeignKey("author.id", ondelete="SET NULL"), index=True, nullable=True
    )
    committer_id = db.Column(
        GUID, db.ForeignKey("author.id", ondelete="SET NULL"), index=True, nullable=True
    )
    message = db.Column(db.Text, nullable=True)
    parents = db.Column(ARRAY(db.String(40)), nullable=True)
    branches = db.Column(ARRAY(db.String(128)), nullable=True)
    date_created = db.Column(
        db.TIMESTAMP(timezone=True),
        default=timezone.now,
        server_default=func.now(),
        nullable=False,
    )
    date_committed = db.Column(
        db.TIMESTAMP(timezone=True),
        default=timezone.now,
        server_default=func.now(),
        nullable=False,
    )

    author = db.relationship("Author", foreign_keys=[author_id])
    committer = db.relationship("Author", foreign_keys=[committer_id])

    __tablename__ = "revision"
    __table_args__ = (db.UniqueConstraint("repository_id", "sha", name="unq_revision"),)
    __repr__ = model_repr("repository_id", "sha", "subject")

    @property
    def subject(self):
        return self.message.splitlines()[0]

    def generate_diff(self):
        from zeus.vcs.base import UnknownRevision

        try:
            vcs = self.repository.get_vcs()
        except UnknownRepositoryBackend:
            return None

        try:
            try:
                return vcs.export(self.sha)
            except UnknownRevision:
                vcs.update()
                return vcs.export(self.sha)
        except Exception:
            current_app.logger.exception("generate_diff failure")
