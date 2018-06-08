from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.types import GUID, JSONEncodedDict
from zeus.db.utils import model_repr


class Source(RepositoryBoundMixin, StandardAttributes, db.Model):
    """
    A source represents the canonical parameters that a build is running against.
    """

    patch_id = db.Column(GUID, db.ForeignKey("patch.id"), unique=True, nullable=True)
    revision_sha = db.Column(db.String(40), nullable=False)
    data = db.Column(JSONEncodedDict, nullable=True)
    author_id = db.Column(GUID, db.ForeignKey("author.id"), index=True)

    author = db.relationship("Author")
    patch = db.relationship("Patch")
    revision = db.relationship(
        "Revision",
        foreign_keys="[Source.repository_id, Source.revision_sha]",
        viewonly=True,
    )

    __tablename__ = "source"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ("repository_id", "revision_sha"),
            ("revision.repository_id", "revision.sha"),
        ),
        db.Index("idx_source_repo_sha", "repository_id", "revision_sha"),
        db.UniqueConstraint(
            "repository_id", "revision_sha", "patch_id", name="unq_source_revision"
        ),
    )
    __repr__ = model_repr("repository_id", "revision_sha", "patch_id")

    def is_commit(self):
        return self.patch_id is None and self.revision_sha

    def generate_diff(self):
        if self.patch:
            return self.patch.diff

        vcs = self.repository.get_vcs()
        if vcs:
            try:
                return vcs.export(self.revision_sha)

            except Exception:
                pass

        return None
