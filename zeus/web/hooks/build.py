from flask import request

from zeus.api.utils.upserts import upsert_build

from .base import BaseHook


class BuildHook(BaseHook):

    def post(self, hook, build_xid):
        return upsert_build(
            repository=hook.repository,
            provider=hook.provider,
            external_id=build_xid,
            data=request.get_json() or {},
        )
