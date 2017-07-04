from __future__ import absolute_import, division, unicode_literals

from zeus.models import Repository

from .base import Resource
from ..schemas import RepositorySchema

repos_schema = RepositorySchema(many=True, strict=True)


class RepositoryIndexResource(Resource):
    def get(self):
        """
        Return a list of repositories.
        """
        query = Repository.query.all()
        return repos_schema.dump(query).data
