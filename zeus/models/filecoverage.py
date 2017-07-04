from datetime import datetime

from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin
from zeus.db.types import GUID


class FileCoverage(RepositoryBoundMixin, db.Model):
    id = db.Column(GUID, nullable=False, primary_key=True,
                   default=GUID.default_value)
    job_id = db.Column(GUID, db.ForeignKey(
        'job.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(256), nullable=False, primary_key=True)
    data = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    lines_covered = db.Column(db.Integer)
    lines_uncovered = db.Column(db.Integer)
    diff_lines_covered = db.Column(db.Integer)
    diff_lines_uncovered = db.Column(db.Integer)

    job = db.relationship('Job', innerjoin=True, uselist=False)

    __tablename__ = 'filecoverage'
    __table_args__ = (
        db.UniqueConstraint('job_id', 'filename', name='unq_job_filname'),
    )
