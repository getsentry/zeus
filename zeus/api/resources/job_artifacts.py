from base64 import b64decode
from io import BytesIO
from flask import request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from werkzeug.datastructures import FileStorage

from zeus.config import db
from zeus.constants import Result, Status
from zeus.models import Artifact, Job
from zeus.tasks import process_artifact

from .base_job import BaseJobResource
from ..schemas import ArtifactSchema

artifact_schema = ArtifactSchema()
artifacts_schema = ArtifactSchema(many=True)


class JobArtifactsResource(BaseJobResource):
    def select_resource_for_update(self):
        return False

    def get(self, job: Job):
        """
        Return a list of artifacts for a given job.
        """
        query = (
            Artifact.query.options(
                joinedload("job"),
                joinedload("job").joinedload("build"),
                joinedload("job").joinedload("build").joinedload("repository"),
            )
            .filter(Artifact.job_id == job.id)
            .order_by(Artifact.name.asc())
        )

        return self.respond_with_schema(artifacts_schema, query)

    def post(self, job: Job):
        """
        Create a new artifact for the given job.

        File can either be passed via standard multi-part form-data, or as a JSON value:

        >>> {
        >>>   "name": "junit.xml",
        >>>   "file": <base64-encoded string>
        >>> }
        """
        # dont bother storing artifacts for aborted jobs
        if job.result == Result.aborted:
            return self.error("job was aborted", status=410)

        if request.content_type == "application/json":
            # file must be base64 encoded
            file_data = request.json.get("file")
            if not file_data:
                return self.respond({"file": "Missing file content."}, status=403)

            file = FileStorage(BytesIO(b64decode(file_data)), request.json.get("name"))
        else:
            try:
                file = request.files["file"]
            except KeyError:
                return self.respond(
                    {"file": "Missing data for required field."}, status=403
                )

        artifact = self.schema_from_request(artifact_schema)
        artifact.job_id = job.id
        artifact.repository_id = job.repository_id
        artifact.status = Status.queued

        if not artifact.name:
            artifact.name = file.filename

        if not artifact.name:
            return self.respond(
                {"name": "Missing data for required field."}, status=403
            )

        try:
            db.session.add(artifact)
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            exists = True
        else:
            exists = False

        if exists:
            # XXX(dcramer): this is more of an error but we make an assumption
            # that this happens because it was already sent
            return self.error("An artifact with this name already exists", 204)

        artifact.file.save(
            file,
            "{0}/{1}/{2}_{3}".format(
                job.id.hex[:4], job.id.hex[4:], artifact.id.hex, artifact.name
            ),
        )
        db.session.add(artifact)
        db.session.commit()

        process_artifact.delay(artifact_id=artifact.id)

        return self.respond_with_schema(artifact_schema, artifact, 201)
