from flask import redirect, Response

from zeus.models import Artifact

from .base_artifact import BaseArtifactResource


class ArtifactDownloadResource(BaseArtifactResource):

    def get(self, artifact: Artifact):
        """
        Streams an artifact file to the client.
        """
        return redirect(artifact.file.url_for(expire=30), code=302, Response=Response)
