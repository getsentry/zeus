from base64 import b64decode
from io import BytesIO

from zeus.config import db
from zeus.constants import Status
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.types import Enum, File, FileData, GUID
from zeus.utils import timezone


class Artifact(RepositoryBoundMixin, StandardAttributes, db.Model):
    job_id = db.Column(
        GUID, db.ForeignKey("job.id", ondelete="CASCADE"), nullable=False
    )
    testcase_id = db.Column(
        GUID, db.ForeignKey("testcase.id", ondelete="CASCADE"), nullable=True
    )
    name = db.Column(db.String(length=256), nullable=False)
    type = db.Column(db.String(length=64), nullable=True)
    file = db.Column(
        File(path="artifacts"),
        nullable=False,
        # TODO(dcramer): this is super hacky but not sure a better way to
        # do it with SQLAlchemy
        default=lambda: FileData({}, default_path="artifacts"),
    )
    status = db.Column(Enum(Status), nullable=False, default=Status.unknown)
    date_started = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    date_updated = db.Column(
        db.TIMESTAMP(timezone=True), nullable=True, onupdate=timezone.now
    )
    date_finished = db.Column(db.TIMESTAMP(timezone=True), nullable=True)

    job = db.relationship("Job", innerjoin=True, uselist=False)
    testcase = db.relationship("TestCase", uselist=False)

    __tablename__ = "artifact"

    def save_base64_content(self, base64):
        content = b64decode(base64)
        self.file.save(
            BytesIO(content),
            "{0}/{1}_{2}".format(self.job_id.hex, self.id.hex, self.name),
        )
