from flask import send_file

from zeus.models import Artifact

from .base_artifact import BaseArtifactResource


class ArtifactDownloadResource(BaseArtifactResource):
    def get(self, artifact: Artifact):
        """
        Streams an artifact file to the client.
        """
        return send_file(
            artifact.file.get_file(),
            attachment_filename=artifact.file.filename,
            as_attachment=True,
        )
