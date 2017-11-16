from zeus.config import db
from zeus.constants import Severity
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.types import Enum, GUID
from zeus.db.utils import model_repr


class StyleViolation(RepositoryBoundMixin, StandardAttributes, db.Model):
    """
    A single style violation.
    """
    job_id = db.Column(GUID, db.ForeignKey(
        'job.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.Text, nullable=False)
    severity = db.Column(Enum(Severity), default=Severity.error, nullable=False)
    message = db.Column(db.Text, nullable=False)
    lineno = db.Column(db.Integer, nullable=True)
    colno = db.Column(db.Integer, nullable=True)
    source = db.Column(db.Text, nullable=True)

    job = db.relationship('Job')

    __tablename__ = 'styleviolation'
    __repr__ = model_repr('repository_id', 'job_id', 'filename', 'message')
