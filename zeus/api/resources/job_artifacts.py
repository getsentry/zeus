from flask import request
from sqlalchemy.exc import IntegrityError

from zeus.config import db
from zeus.constants import Result
from zeus.models import Job, Artifact

from .base import Resource
from ..schemas import ArtifactSchema

artifact_schema = ArtifactSchema(strict=True)
artifacts_schema = ArtifactSchema(strict=True, many=True)


class JobArtifactsResource(Resource):
    def get(self, job_id: str):
        """
        Return a list of artifacts for a given job.
        """
        job = Job.query.get(job_id)
        if not job:
            return self.not_found()

        query = Artifact.query.filter(
            Artifact.job_id == job.id,
        )

        return self.respond_with_schema(artifacts_schema, query)

    def post(self, job_id: str):
        """
        Create a new artifact for the given job.
        """
        job = Job.query.get(job_id)
        if not job:
            return self.not_found()

        # dont bother storing artifacts for aborted jobs
        if job.result == Result.aborted:
            return self.error('job was aborted', status=410)

        try:
            file = request.files['file']
        except KeyError:
            return self.respond({'file': 'Missing data for required field.'}, status=403)

        result = self.schema_from_request(artifact_schema)
        artifact = result.data
        artifact.job_id = job.id
        artifact.repository_id = job.repository_id

        if not artifact.name:
            artifact.name = file.filename

        if not artifact.name:
            return self.respond({'name': 'Missing data for required field.'}, status=403)

        try:
            db.session.add(artifact)
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            exists = True
        else:
            exists = False

        if exists:
            # XXX(dcramer); this is more of an error but we make an assumption
            # that this happens because it was already sent
            return self.error('An artifact with this name already exists', 204)

        # TODO(dcramer): send to queue for processing
        artifact.file.save(
            request.files['file'],
            '{0}/{1}/{2}_{3}'.format(
                job.id.hex[:4], job.id.hex[4:], artifact.id.hex, artifact.name
            ),
        )
        db.session.add(artifact)
        db.session.commit()

        return self.respond_with_schema(artifact_schema, artifact, 201)
