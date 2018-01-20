from flask import request

from zeus.api.utils.upserts import upsert_change_request

from .base import BaseHook


class ChangeRequestHook(BaseHook):
    def post(self, hook, cr_xid):
        return upsert_change_request(
            provider=hook.provider,
            external_id=cr_xid,
            data=request.get_json() or {},
        )
