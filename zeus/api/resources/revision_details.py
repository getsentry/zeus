from zeus.models import Revision
from zeus.utils.builds import fetch_build_for_revision

from .base_revision import BaseRevisionResource
from ..schemas import BuildSchema

build_schema = BuildSchema(strict=True)


class RevisionDetailsResource(BaseRevisionResource):
    def select_resource_for_update(self) -> bool:
        return False

    def get(self, revision: Revision, repo=None):
        """
        Return the joined build status of a revision.
        """
        build = fetch_build_for_revision(revision.repository, revision)
        if not build:
            return self.respond(status=404)
        return self.respond_with_schema(build_schema, build)
