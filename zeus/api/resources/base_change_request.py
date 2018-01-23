from flask import request, Response
from sqlalchemy.orm import contains_eager

from zeus import auth
from zeus.constants import PERMISSION_MAP
from zeus.models import ChangeRequest, Repository, RepositoryProvider

from .base import Resource


class BaseChangeRequestResource(Resource):
    def dispatch_request(
        self, provider: str, owner_name: str, repo_name: str, cr_number: int, *args, **kwargs
    ) -> Response:
        queryset = ChangeRequest.query.join(Repository, Repository.id == ChangeRequest.repository_id).filter(
            Repository.provider == RepositoryProvider(provider),
            Repository.owner_name == owner_name,
            Repository.name == repo_name,
            ChangeRequest.number == cr_number,
        )
        if self.select_resource_for_update():
            queryset = queryset.with_for_update()
        else:
            # HACK(dcramer): we dont want to lock the repo row, so for now just deal
            # w/ the consequences of this
            queryset = queryset.options(
                contains_eager('repository'),
            )
        cr = queryset.first()
        if not cr:
            return self.not_found()
        tenant = auth.get_current_tenant()
        if not tenant.has_permission(cr.repository_id, PERMISSION_MAP[request.method]):
            return self.error('permission denied', 400)
        return Resource.dispatch_request(self, cr, *args, **kwargs)
