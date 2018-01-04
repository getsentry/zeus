from sqlalchemy.dialects.postgresql import ARRAY

from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.types import GUID
from zeus.db.utils import model_repr


class WebpackAsset(RepositoryBoundMixin, StandardAttributes, db.Model):
    job_id = db.Column(GUID, db.ForeignKey(
        'job.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.Text, nullable=False)
    size = db.Column(db.Integer, nullable=True)
    chunk_names = db.Column(ARRAY(db.String), nullable=True)

    job = db.relationship('Job')

    __tablename__ = 'webpack_asset'
    __table_args__ = (db.UniqueConstraint(
        'job_id', 'filename', name='unq_webpack_asset'), )
    __repr__ = model_repr('repository_id', 'job_id', 'filename')


class WebpackEntrypoint(RepositoryBoundMixin, StandardAttributes, db.Model):
    job_id = db.Column(GUID, db.ForeignKey(
        'job.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    asset_names = db.Column(ARRAY(db.String), nullable=True)

    job = db.relationship('Job')

    __tablename__ = 'webpack_entrypoint'
    __table_args__ = (db.UniqueConstraint(
        'job_id', 'name', name='unq_webpack_entrypoint'), )
    __repr__ = model_repr('repository_id', 'job_id', 'name')
