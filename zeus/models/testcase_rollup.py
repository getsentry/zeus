from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin
from zeus.db.types import GUID
from zeus.db.utils import model_repr


class TestCaseRollup(RepositoryBoundMixin, db.Model):
    """
    A daily rollup of test case results for a given repository.
    """

    id = db.Column(GUID, nullable=False, primary_key=True, default=GUID.default_value)
    hash = db.Column(db.String(40), nullable=False)
    name = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_runs = db.Column(db.Integer, default=0, nullable=False)
    total_duration = db.Column(db.Integer, default=0, nullable=False)
    runs_failed = db.Column(db.Integer, default=0, nullable=False)
    runs_passed = db.Column(db.Integer, default=0, nullable=False)

    __tablename__ = "testcase_rollup"
    __table_args__ = (
        db.UniqueConstraint(
            "repository_id", "hash", "date", name="unq_testcase_rollup_hash"
        ),
    )
    __repr__ = model_repr("repository_id", "name", "date")
