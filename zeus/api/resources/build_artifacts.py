from zeus.models import Artifact, Build, Job

from .base_build import BaseBuildResource
from ..schemas import ArtifactSchema

artifact_schema = ArtifactSchema(strict=True)
artifacts_schema = ArtifactSchema(strict=True, many=True)


class BuildArtifactsResource(BaseBuildResource):
    def get(self, build: Build):
        """
        Return a list of artifacts for a given build.
        """
        query = Artifact.query.join(Job, Job.id == Artifact.job_id).filter(
            Job.build_id == build.id,
        ).order_by(Artifact.name.asc())

        return self.respond_with_schema(artifacts_schema, query)
