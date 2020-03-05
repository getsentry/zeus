from sqlalchemy import event
from sqlalchemy.sql import func, select

from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.types import GUID, JSONEncodedDict
from zeus.db.utils import model_repr
from zeus.utils import timezone


change_request_author_table = db.Table(
    "change_request_author",
    db.Column(
        "change_request_id",
        GUID,
        db.ForeignKey("change_request.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "author_id",
        GUID,
        db.ForeignKey("author.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class ChangeRequest(RepositoryBoundMixin, StandardAttributes, db.Model):
    number = db.Column(db.Integer, nullable=False)
    # the parent revision is our base commit that this change request applies to
    parent_ref = db.Column(db.String, nullable=True)
    parent_revision_sha = db.Column(db.String(40), nullable=True)
    # for branch-style change requests (e.g. GitHub Pull Requests) we capture
    # the 'current revision' in addition to the 'parent revision'
    head_ref = db.Column(db.String, nullable=True)
    head_revision_sha = db.Column(db.String(40), nullable=True)
    message = db.Column(db.String, nullable=False)
    author_id = db.Column(
        GUID, db.ForeignKey("author.id", ondelete="SET NULL"), index=True, nullable=True
    )
    provider = db.Column(db.String, nullable=True)
    external_id = db.Column(db.String(64), nullable=True)
    url = db.Column(db.String, nullable=True)
    data = db.Column(JSONEncodedDict, nullable=True)
    date_updated = db.Column(
        db.TIMESTAMP(timezone=True), nullable=True, onupdate=timezone.now
    )

    head_revision = db.relationship(
        "Revision",
        foreign_keys="[ChangeRequest.repository_id, ChangeRequest.head_revision_sha]",
        viewonly=True,
    )
    parent_revision = db.relationship(
        "Revision",
        foreign_keys="[ChangeRequest.repository_id, ChangeRequest.parent_revision_sha]",
        viewonly=True,
    )
    authors = db.relationship(
        "Author", secondary=change_request_author_table, backref="change_requests"
    )

    __tablename__ = "change_request"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ("repository_id", "parent_revision_sha"),
            ("revision.repository_id", "revision.sha"),
        ),
        db.ForeignKeyConstraint(
            ("repository_id", "head_revision_sha"),
            ("revision.repository_id", "revision.sha"),
        ),
        db.Index("idx_cr_parent_revision", "repository_id", "parent_revision_sha"),
        db.Index("idx_cr_head_revision", "repository_id", "head_revision_sha"),
        db.UniqueConstraint("repository_id", "number", name="unq_cr_number"),
        db.UniqueConstraint(
            "repository_id", "provider", "external_id", name="unq_cr_provider"
        ),
    )
    __repr__ = model_repr("repository_id", "parent_revision_sha")

    @property
    def subject(self):
        return self.message.splitlines()[0]


@event.listens_for(ChangeRequest.repository_id, "set", retval=False)
def set_number(target, value, oldvalue, initiator):
    if value is not None and target.number is None:
        target.number = select([func.next_item_value(value)])
    return value
