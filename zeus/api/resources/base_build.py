from flask import Response

from sqlalchemy.orm import contains_eager
from zeus.models import Build, Repository, RepositoryProvider

from .base import Resource


class BaseBuildResource(Resource):
    def dispatch_request(
        self, provider: str, owner_name: str, repo_name: str, build_number: int, *args, **kwargs
    ) -> Response:
        queryset = Build.query.options(
            contains_eager('repository'),
        ).join(Repository, Repository.id == Build.repository_id).filter(
            Repository.provider == RepositoryProvider(provider),
            Repository.owner_name == owner_name,
            Repository.name == repo_name,
            Build.number == build_number,
        )
        if self.select_resurce_for_update():
            queryset = queryset.with_for_update()
        build = queryset.first()
        if not build:
            return self.not_found()
        return Resource.dispatch_request(self, build, *args, **kwargs)
