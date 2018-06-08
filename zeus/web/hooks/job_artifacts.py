from flask import request

from zeus.models import Build, Job
from zeus.api import client

from .base import BaseHook


class JobArtifactsHook(BaseHook):
    def post(self, hook, build_xid, job_xid):
        build = Build.query.filter(
            Build.provider == hook.provider, Build.external_id == build_xid
        ).first()
        if not build:
            return self.respond("", 404)

        job = Job.query.filter(
            Job.provider == hook.provider,
            Job.external_id == job_xid,
            Job.build_id == build.id,
        ).first()
        if not job:
            return self.respond("", 404)

        return client.post(
            "/repos/{}/builds/{}/jobs/{}/artifacts".format(
                hook.repository.get_full_name(), job.build.number, job.number
            ),
            request=request,
        )
