from sqlalchemy.orm import joinedload
from marshmallow import fields

from zeus.models import Artifact, Build, Job

from .base_build import BaseBuildResource
from ..schemas import ArtifactSchema, JobSchema


class ArtifactWithJobSchema(ArtifactSchema):
    job = fields.Nested(
        JobSchema(exclude=("stats", "failures")), dump_only=True, required=False
    )


artifacts_schema = ArtifactWithJobSchema(many=True)


class BuildArtifactsResource(BaseBuildResource):
    def get(self, build: Build):
        """
        Return a list of artifacts for a given build.
        """
        query = (
            Artifact.query.options(
                joinedload("job"),
                joinedload("job").joinedload("build"),
                joinedload("job").joinedload("build").joinedload("repository"),
            )
            .join(Job, Job.id == Artifact.job_id)
            .filter(Job.build_id == build.id)
            .order_by(Artifact.name.asc())
        )

        return self.respond_with_schema(artifacts_schema, query)
