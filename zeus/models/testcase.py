import re

from hashlib import sha1
from sqlalchemy import event

from zeus.config import db
from zeus.constants import Result
from zeus.db.mixins import ProjectBoundMixin
from zeus.db.types import Enum, GUID
from zeus.db.utils import model_repr


class TestCase(ProjectBoundMixin, db.Model):
    """
    A single run of a single test.
    """
    id = db.Column(GUID, nullable=False, primary_key=True, default=GUID.default_value)
    job_id = db.Column(GUID, db.ForeignKey('job.id', ondelete="CASCADE"), nullable=False)
    hash = db.Column(db.String(40), nullable=False)
    name = db.Column(db.Text, nullable=False)
    result = db.Column(Enum(Result), default=Result.unknown, nullable=False)
    # duration, in milliseconds
    duration = db.Column(db.Integer, default=0, nullable=True)
    message = db.deferred(db.Column(db.Text, nullable=True))

    job = db.relationship('Job')

    __tablename__ = 'testcase'
    __table_args__ = (db.UniqueConstraint('job_id', 'hash', name='unq_testcase_hash'), )
    __repr__ = model_repr('job_id', 'name', 'result')

    @classmethod
    def calculate_sha(self, name):
        assert name
        return sha1(name.encode('utf-8')).hexdigest()

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
    if new_sha != target.hash:
        target.hash = new_sha
    return value
