from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin
from zeus.db.types import GUID
from zeus.db.utils import model_repr


class FileCoverage(RepositoryBoundMixin, db.Model):
    id = db.Column(GUID, nullable=False, primary_key=True, default=GUID.default_value)
    build_id = db.Column(
        GUID, db.ForeignKey("build.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename = db.Column(db.String(256), nullable=False, primary_key=True)
    data = db.Column(db.Text, nullable=False)

    lines_covered = db.Column(db.Integer, nullable=False)
    lines_uncovered = db.Column(db.Integer, nullable=False)
    diff_lines_covered = db.Column(db.Integer, nullable=False)
    diff_lines_uncovered = db.Column(db.Integer, nullable=False)

    build = db.relationship("Build", innerjoin=True, uselist=False)

    __tablename__ = "filecoverage"
    __table_args__ = (
        db.UniqueConstraint("build_id", "filename", name="unq_coverage_filname"),
    )
    __repr__ = model_repr("repository_id", "build_id", "filename")
