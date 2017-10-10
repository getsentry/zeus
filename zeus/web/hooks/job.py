from flask import request

from zeus.config import redis
from zeus.models import Build, Job
from zeus.api import client

from .base import BaseHook


class JobHook(BaseHook):
    def post(self, hook, build_xid, job_xid):
        build = Build.query.filter(
            Build.provider == hook.provider,
            Build.external_id == build_xid,
        ).first()
        if not build:
            return self.respond('', 404)

        lock_key = 'hook:job:{hook_id}:{build_xid}:{job_xid}'.format(
            hook_id=hook.id.hex,
            build_xid=build_xid,
            job_xid=job_xid,
        )
        with redis.lock(lock_key):
            job = Job.query.filter(
                Job.provider == hook.provider,
                Job.external_id == job_xid,
                Job.build_id == build.id,
            ).first()

            json = request.get_json() or {}
            json['external_id'] = job_xid
            json['provider'] = hook.provider

            if job:
                response = client.put(
                    '/repos/{}/builds/{}/jobs/{}'.format(
                        hook.repository.get_full_name(),
                        job.build.number,
                        job.number,
                    ),
                    json=json
                )
            else:
                response = client.post(
                    '/repos/{}/builds/{}/jobs'.format(
                        hook.repository.get_full_name(),
                        build.number,
                    ),
                    json=json
                )

            return response
