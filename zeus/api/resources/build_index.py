from __future__ import absolute_import, division, unicode_literals

from zeus.models import Build

from .base import Resource
from ..schemas import BuildSchema

builds_schema = BuildSchema(many=True, strict=True)


class BuildIndexResource(Resource):
    def get(self):
        """
        Return a list of builds.
        """
        query = Build.query.all()
        return builds_schema.dump(query).data
