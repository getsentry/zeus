from flask import request
from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import FileStorage
from base64 import b64decode
from io import BytesIO

from zeus.api import client
from zeus.api.schemas import PendingArtifactSchema
from zeus.config import db
from zeus.constants import Status
from zeus.models import Build, Job


from .base import BaseHook

pending_artifact_schema = PendingArtifactSchema()


class JobArtifactsHook(BaseHook):
    def handle_async(self, hook, build_xid, job_xid):
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

        artifact = self.schema_from_request(pending_artifact_schema)
        artifact.external_build_id = build_xid
        artifact.external_job_id = job_xid
        artifact.provider = hook.provider
        artifact.repository_id = hook.repository_id
        artifact.status = Status.queued
        artifact.hook_id = hook.id

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
                job_xid[:4], job_xid[4:], artifact.id.hex, artifact.name
            ),
        )
        db.session.add(artifact)
        db.session.commit()

        return self.respond_with_schema(pending_artifact_schema, artifact, 202)

    def post(self, hook, build_xid, job_xid):
        provider_name = hook.get_provider().get_name(hook.config)
        build = Build.query.filter(
            Build.provider == provider_name, Build.external_id == build_xid
        ).first()
        if not build:
            return self.handle_async(hook, build_xid, job_xid)

        job = Job.query.filter(
            Job.provider == provider_name,
            Job.external_id == job_xid,
            Job.build_id == build.id,
        ).first()
        if not job:
            return self.handle_async(hook, build_xid, job_xid)

        return client.post(
            "/repos/{}/builds/{}/jobs/{}/artifacts".format(
                hook.repository.get_full_name(), job.build.number, job.number
            ),
            request=request,
        )
