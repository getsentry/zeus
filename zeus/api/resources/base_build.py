from flask import Response

from zeus.models import Build, Repository

from .base import Resource


class BaseBuildResource(Resource):
    def dispatch_request(
        self, repository_name: str, build_number: int, *args, **kwargs
    ) -> Response:
        build = Build.query.join(Repository, Repository.id == Build.repository_id).filter(
            Repository.name == repository_name,
            Build.number == build_number,
        ).first()
        if not build:
            return self.not_found()
        return Resource.dispatch_request(self, build, *args, **kwargs)
