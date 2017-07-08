from __future__ import absolute_import, division, unicode_literals

from flask import request
from sqlalchemy.exc import IntegrityError

from zeus.config import db
from zeus.constants import Result
from zeus.models import Job, Artifact

from .base import Resource
from ..schemas import ArtifactSchema

artifacts_schema = ArtifactSchema(strict=True)


class JobArtifactsResource(Resource):
    def get(self, job_id):
        """
        Return a list of artifacts for a given job.
        """
        job = Job.query.get(job_id)
        if not job:
            return self.not_found()

        query = Artifact.query.filter(
            Artifact.job_id == job.id, )

        return artifacts_schema.dump(query).data

    def post(self, job_id):
        """
        Create a new artifact for the given job.
        """
        job = Job.query.get(job_id)
        if not job:
            return self.not_found()

        # dont bother storing artifacts for aborted jobs
        if job.result == Result.aborted:
            return self.error('job was aborted', status=410)

        data = artifacts_schema.load(request.get_json())

        artifact = Artifact(
            name=data['name'],
            job_id=job.id, )
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

        # TODO(dcramer): save file and then send to queue for processing
        # artifact.file.save(
        #     args.artifact_file,
        #     '{0}/{1}/{2}_{3}'.format(
        #         step_id[:4], step_id[4:],
        #         artifact.id.hex, artifact.name
        #     ),
        # )
        # db.session.add(artifact)
        # db.session.commit()

        return self.respond(artifacts_schema.dump(artifact).data, 201)
