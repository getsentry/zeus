from zeus.models import Revision
from zeus.utils.builds import fetch_builds_for_revisions

from .base_revision import BaseRevisionResource
from ..schemas import BuildSchema

build_schema = BuildSchema(strict=True)


class RevisionDetailsResource(BaseRevisionResource):
    def select_resurce_for_update(self) -> bool:
        return self.is_mutation()

    def get(self, revision: Revision, repo=None):
        """
        Return the joined build status of a revision.
        """
        (_, build) = fetch_builds_for_revisions(
            revision.repository, [revision.sha])
        return self.respond_with_schema(build_schema, build)
