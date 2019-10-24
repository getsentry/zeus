from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.types import File, FileData, GUID


class PendingArtifact(RepositoryBoundMixin, StandardAttributes, db.Model):
    provider = db.Column(db.String, nullable=False)
    external_job_id = db.Column(db.String(64), nullable=False)
    external_build_id = db.Column(db.String(64), nullable=False)
    hook_id = db.Column(
        GUID, db.ForeignKey("hook.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = db.Column(db.String(length=256), nullable=False)
    type = db.Column(db.String(length=64), nullable=True)
    file = db.Column(
        File(path="artifacts"),
        nullable=False,
        # TODO(dcramer): this is super hacky but not sure a better way to
        # do it with SQLAlchemy
        default=lambda: FileData({}, default_path="artifacts"),
    )

    hook = db.relationship("Hook")

    __tablename__ = "pending_artifact"
    __table_args__ = (
        db.Index(
            "idx_pending_artifact",
            "repository_id",
            "provider",
            "external_job_id",
            "external_build_id",
        ),
    )
