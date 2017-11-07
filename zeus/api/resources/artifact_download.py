from flask import Response

from zeus.models import Artifact

from .base_artifact import BaseArtifactResource


class ArtifactDownloadResource(BaseArtifactResource):
    def get(self, artifact: Artifact):
        """
        Streams an artifact file to the client.
        """
        return Response(artifact.file.get_file())
