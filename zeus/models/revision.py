
from flask import current_app
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func

from zeus.config import db
from zeus.db.mixins import RepositoryBoundQuery
from zeus.db.types import GUID
from zeus.db.utils import model_repr
from zeus.exceptions import UnknownRepositoryBackend
from zeus.utils import timezone


revision_author_table = db.Table(
    "revision_author",
    db.Column(
        "repository_id",
        GUID,
        db.ForeignKey("repository.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column("revision_sha", db.String(40), primary_key=True),
    db.Column(
        "author_id",
        GUID,
        db.ForeignKey("author.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.ForeignKeyConstraint(
        ("repository_id", "revision_sha"),
        ("revision.repository_id", "revision.sha"),
        ondelete="CASCADE",
    ),
)


class Revision(db.Model):
    # XXX(dcramer): the primary_key doesnt include repo_id at the moment, which is wrong, but
    # we need to deal w/ that in a followup change
    repository_id = db.Column(
        GUID, db.ForeignKey("repository.id", ondelete="CASCADE"), primary_key=True
    )
    sha = db.Column(db.String(40), primary_key=True)
    author_id = db.Column(
        GUID, db.ForeignKey("author.id", ondelete="SET NULL"), index=True, nullable=True
    )
    committer_id = db.Column(
        GUID, db.ForeignKey("author.id", ondelete="SET NULL"), index=True, nullable=True
    )
    message = db.Column(db.Text, nullable=True)
    parents = db.Column(ARRAY(db.String(40)), nullable=True)
    # TODO: remove this column, we dont use it and its wrong
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
    authors = db.relationship(
        "Author", secondary=revision_author_table, backref="revisions"
    )
    committer = db.relationship("Author", foreign_keys=[committer_id])
    repository = db.relationship("Repository", foreign_keys=[repository_id])

    query_class = RepositoryBoundQuery

    __tablename__ = "revision"
    # XXX(dcramer): the primary_key doesnt include repo_id at the moment, which is wrong, but
    # we need to deal w/ that in a followup change
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
