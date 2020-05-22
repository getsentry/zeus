from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin
from zeus.db.types import GUID
from zeus.db.utils import model_repr


class TestCaseMeta(RepositoryBoundMixin, db.Model):
    """
    A materialized view of a testcase's historical properties.
    """

    id = db.Column(GUID, nullable=False, primary_key=True, default=GUID.default_value)
    hash = db.Column(db.String(40), nullable=False)
    name = db.Column(db.Text, nullable=False)
    first_build_id = db.Column(
        GUID, db.ForeignKey("build.id", ondelete="CASCADE"), nullable=False
    )

    first_build = db.relationship("Build")

    __tablename__ = "testcase_meta"
    __table_args__ = (
        db.UniqueConstraint("repository_id", "hash", name="unq_testcase_meta_hash"),
    )
    __repr__ = model_repr("repository_id", "name")
