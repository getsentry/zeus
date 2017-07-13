import enum

from base64 import b64decode
from io import BytesIO

from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.types import Enum, File, FileData, GUID

ARTIFACT_STORAGE_OPTIONS = {
    'path': 'artifacts',
}


class ArtifactType(enum.Enum):
    UNKNOWN = 0
    TEXT = 1
    IMAGE = 2
    HTML = 3

    def __str__(self):
        return self.name


class Artifact(RepositoryBoundMixin, StandardAttributes, db.Model):
    job_id = db.Column(GUID, db.ForeignKey('job.id', ondelete='CASCADE'), nullable=False)
    testcase_id = db.Column(GUID, db.ForeignKey('testcase.id', ondelete='CASCADE'), nullable=True)
    name = db.Column(db.String(length=256), nullable=False)
    type = db.Column(
        Enum(ArtifactType), default=ArtifactType.UNKNOWN, nullable=False, server_default='0'
    )
    file = db.Column(
        File(**ARTIFACT_STORAGE_OPTIONS),
        nullable=False,
        # TODO(dcramer): this is super hacky but not sure a better way to
        # do it with SQLAlchemy
        default=lambda: FileData({}, ARTIFACT_STORAGE_OPTIONS)
    )

    job = db.relationship('Job', innerjoin=True, uselist=False)
    testcase = db.relationship('TestCase', uselist=False)

    __tablename__ = 'artifact'

    def save_base64_content(self, base64):
        content = b64decode(base64)
        self.file.save(
            BytesIO(content), '{0}/{1}_{2}'.format(self.job_id.hex, self.id.hex, self.name)
        )
