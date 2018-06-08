from sqlalchemy.orm import joinedload
from marshmallow import fields

from zeus.models import Artifact, Job, Revision
from zeus.utils.builds import fetch_build_for_revision

from .base_revision import BaseRevisionResource
from ..schemas import ArtifactSchema, JobSchema


class ArtifactWithJobSchema(ArtifactSchema):
    job = fields.Nested(JobSchema(), dump_only=True, required=False)


artifacts_schema = ArtifactWithJobSchema(strict=True, many=True)


class RevisionArtifactsResource(BaseRevisionResource):
    def select_resource_for_update(self) -> bool:
        return False

    def get(self, revision: Revision, repo=None):
        """
        Return all artifacts of all builds in a revision.
        """
        build = fetch_build_for_revision(revision.repository, revision)
        if not build:
            return self.respond(status=404)

        build_ids = [original.id for original in build.original]

        query = (
            Artifact.query.options(
                joinedload("job"),
                joinedload("job").joinedload("build"),
                joinedload("job").joinedload("build").joinedload("source"),
                joinedload("job")
                .joinedload("build")
                .joinedload("source")
                .joinedload("repository"),
            )
            .join(Job, Job.id == Artifact.job_id)
            .filter(Job.build_id.in_(build_ids))
            .order_by(Artifact.name.asc())
        )

        return self.respond_with_schema(artifacts_schema, query)
