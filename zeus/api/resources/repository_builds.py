from __future__ import absolute_import, division, unicode_literals

from zeus.models import Build, Repository

from .base import Resource
from ..schemas import BuildSchema

builds_schema = BuildSchema(many=True, strict=True)


class RepositoryBuildsResource(Resource):
    def get(self, repository_id):
        """
        Return a list of builds for the given repository.
        """
        repo = Repository.query.get(repository_id)
        if not repo:
            return self.not_found()

        query = Build.query.filter(
            Build.repository_id == repository_id,
        )
        return builds_schema.dump(query).data
