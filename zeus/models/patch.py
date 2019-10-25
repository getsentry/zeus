from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.utils import model_repr


class Patch(RepositoryBoundMixin, StandardAttributes, db.Model):
    parent_ref = db.Column(db.String, nullable=False)
    parent_revision_sha = db.Column(db.String(40), nullable=True)
    diff = db.deferred(db.Column(db.Text, nullable=False))

    parent_revision = db.relationship(
        "Revision",
        foreign_keys="[Patch.repository_id, Patch.parent_revision_sha]",
        viewonly=True,
    )

    __tablename__ = "patch"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ("repository_id", "parent_revision_sha"),
            ("revision.repository_id", "revision.sha"),
        ),
        db.Index("idx_repo_sha", "repository_id", "parent_revision_sha"),
    )
    __repr__ = model_repr("repository_id", "parent_revision_sha")
