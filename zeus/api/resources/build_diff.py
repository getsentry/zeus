from zeus.models import Build

from .base_build import BaseBuildResource


class BuildDiffResource(BaseBuildResource):
    def get(self, build: Build):
        """
        Return a diff for the given build.
        """
        if not build.revision:
            self.respond({"diff": None})
        return self.respond({"diff": build.revision.generate_diff()})
