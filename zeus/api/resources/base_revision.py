from flask import request, Response

from zeus import auth
from zeus.constants import PERMISSION_MAP
from zeus.models import Repository, RepositoryProvider, Revision

from .base import Resource


class BaseRevisionResource(Resource):
    def dispatch_request(
        self,
        provider,
        owner_name: str,
        repo_name: str,
        revision_sha: str,
        *args,
        **kwargs
    ) -> Response:
        queryset = Revision.query.join(
            Repository, Repository.id == Revision.repository_id
        ).filter(
            Repository.provider == RepositoryProvider(provider),
            Repository.owner_name == owner_name,
            Repository.name == repo_name,
            Revision.sha == revision_sha,
        )
        if self.select_resource_for_update():
            queryset = queryset.with_for_update()
        revision = queryset.first()
        if not revision:
            return self.not_found()

        tenant = auth.get_current_tenant()
        if not tenant.has_permission(
            revision.repository_id, PERMISSION_MAP[request.method]
        ):
            return self.error("permission denied", 400)

        return Resource.dispatch_request(self, revision, *args, **kwargs)
