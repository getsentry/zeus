from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.types import GUID
from zeus.db.utils import model_repr


class Bundle(RepositoryBoundMixin, StandardAttributes, db.Model):
    job_id = db.Column(
        GUID, db.ForeignKey("job.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.Text, nullable=False)

    job = db.relationship("Job")
    assets = db.relationship("BundleAsset", lazy="subquery")

    __tablename__ = "bundle"
    __table_args__ = (db.UniqueConstraint("job_id", "name", name="unq_bundle"),)
    __repr__ = model_repr("repository_id", "job_id", "name")


class BundleAsset(RepositoryBoundMixin, StandardAttributes, db.Model):
    bundle_id = db.Column(
        GUID, db.ForeignKey("bundle.id", ondelete="CASCADE"), nullable=False
    )
    job_id = db.Column(
        GUID, db.ForeignKey("job.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.Text, nullable=False)
    size = db.Column(db.Integer, nullable=True)

    job = db.relationship("Job")
    bundle = db.relationship("Bundle")

    __tablename__ = "bundle_asset"
    __table_args__ = (
        db.UniqueConstraint("bundle_id", "name", name="unq_bundle_asset"),
    )
    __repr__ = model_repr("repository_id", "job_id", "bundle_id", "name")
