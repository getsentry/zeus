from flask import Response
from sqlalchemy.orm import contains_eager

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
        if self.select_resurce_for_update():
            queryset = queryset.with_for_update()
        else:
            # HACK(dcramer): we dont want to lock the repo row, so for now just deal
            # w/ the consequences of this
            queryset = queryset.options(
                contains_eager('repository'),
            )
        build = queryset.first()
        if not build:
            return self.not_found()
        return Resource.dispatch_request(self, build, *args, **kwargs)
