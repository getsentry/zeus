from sqlalchemy.dialects.postgresql import ARRAY

from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.types import GUID
from zeus.db.utils import model_repr


bundle_entrypoint_asset = db.Table(
    'bundle_entrypoint_asset',
    db.Column('entrypoint_id', GUID, db.ForeignKey(
        'bundle_entrypoint.id'), primary_key=True),
    db.Column('asset_id', GUID, db.ForeignKey(
        'bundle_asset.id'), primary_key=True)
)


class BundleAsset(RepositoryBoundMixin, StandardAttributes, db.Model):
    job_id = db.Column(GUID, db.ForeignKey(
        'job.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    size = db.Column(db.Integer, nullable=True)
    chunk_names = db.Column(ARRAY(db.String), nullable=True)

    job = db.relationship('Job')

    __tablename__ = 'bundle_asset'
    __table_args__ = (db.UniqueConstraint(
        'job_id', 'name', name='unq_bundle_asset'), )
    __repr__ = model_repr('repository_id', 'job_id', 'name')


class BundleEntrypoint(RepositoryBoundMixin, StandardAttributes, db.Model):
    job_id = db.Column(GUID, db.ForeignKey(
        'job.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.Text, nullable=False)

    job = db.relationship('Job')
    assets = db.relationship('BundleAsset', secondary=bundle_entrypoint_asset,
                             lazy='subquery', backref=db.backref('entrypoints', lazy=True))

    __tablename__ = 'bundle_entrypoint'
    __table_args__ = (db.UniqueConstraint(
        'job_id', 'name', name='unq_bundle_entrypoint'), )
    __repr__ = model_repr('repository_id', 'job_id', 'name')
