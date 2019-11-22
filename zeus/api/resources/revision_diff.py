from zeus.models import Revision

from .base_revision import BaseRevisionResource


class RevisionDiffResource(BaseRevisionResource):
    def get(self, revision: Revision):
        """
        Return a diff for the given revision.
        """
        return self.respond({"diff": revision.generate_diff()})
