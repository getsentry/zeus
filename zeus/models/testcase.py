import re

from datetime import datetime
from hashlib import sha1
from sqlalchemy import event

from zeus.config import db
from zeus.constants import Result
from zeus.db.mixins import RepositoryBoundMixin
from zeus.db.types import Enum, GUID


class TestCase(RepositoryBoundMixin, db.Model):
    """
    A single run of a single test.
    """
    id = db.Column(GUID, nullable=False, primary_key=True,
                   default=GUID.default_value)
    job_id = db.Column(GUID, db.ForeignKey(
        'job.id', ondelete="CASCADE"), nullable=False)
    hash = db.Column(db.String(40), nullable=False)
    name = db.Column(db.Text, nullable=False)
    result = db.Column(Enum(Result), default=Result.unknown, nullable=False)
    duration = db.Column(db.Integer, default=0)
    message = db.deferred(db.Column(db.Text))
    date_created = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    job = db.relationship('Job')

    __tablename__ = 'test'
    __table_args__ = (
        db.UniqueConstraint('job_id', 'hash', name='unq_test_hash'),
    )

    @classmethod
    def calculate_sha(self, name):
        assert name
        return sha1(name).hexdigest()

    @property
    def sep(self):
        name = self.name
        # handle the case where it might begin with some special character
        if not re.match(r'^[a-zA-Z0-9]', name):
            return '/'
        elif '/' in name:
            return '/'
        return '.'


@event.listens_for(TestCase.name, 'set', retval=False)
def set_name_sha(target, value, oldvalue, initiator):
    if not value:
        return value

    new_sha = TestCase.calculate_sha(value)
    if new_sha != target.sha:
        target.sha = new_sha
    return value
