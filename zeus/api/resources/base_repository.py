from flask import request, Response

from zeus import auth
from zeus.constants import PERMISSION_MAP
from zeus.models import Repository, RepositoryProvider

from .base import Resource


class BaseRepositoryResource(Resource):
    def dispatch_request(
        self, provider, owner_name: str, repo_name: str, *args, **kwargs
    ) -> Response:
        queryset = Repository.query.filter(
            Repository.provider == RepositoryProvider(provider),
            Repository.owner_name == owner_name,
            Repository.name == repo_name,
        )
        if self.select_resource_for_update():
            queryset = queryset.with_for_update()
        repo = queryset.first()
        if not repo:
            return self.not_found()

        tenant = auth.get_current_tenant()
        required_permission = self.permission_overrides.get(
            request.method, PERMISSION_MAP[request.method]
        )

        if not tenant.has_permission(repo.id, required_permission):
            return self.error("permission denied", 400)

        return Resource.dispatch_request(self, repo, *args, **kwargs)
