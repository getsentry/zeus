from flask import request

from zeus.models import Build
from zeus.api.utils.upserts import upsert_job

from .base import BaseHook


class JobHook(BaseHook):
    def post(self, hook, build_xid, job_xid):
        build = Build.query.filter(
            Build.provider == hook.provider, Build.external_id == build_xid
        ).first()
        if not build:
            return self.respond("", 404)

        return upsert_job(
            build=build, hook=hook, external_id=job_xid, data=request.get_json() or {}
        )
