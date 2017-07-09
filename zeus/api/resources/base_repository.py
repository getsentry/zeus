from flask import Response

from zeus.models import Repository

from .base import Resource


class BaseRepositoryResource(Resource):
    def dispatch_request(self, repository_name: str, *args, **kwargs) -> Response:
        repo = Repository.query.filter(Repository.name == repository_name).first()
        if not repo:
            return self.not_found()
        return Resource.dispatch_request(self, repo, *args, **kwargs)
