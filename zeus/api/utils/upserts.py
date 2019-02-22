from flask import Response

from zeus.config import redis
from zeus.models import Repository, Build, ChangeRequest, Hook, Job
from zeus.api import client

BUILD_LOCK_TIMEOUT = 10.0


def upsert_job(
    build: Build, hook: Hook, external_id: str, data: dict = None
) -> Response:
    provider_name = hook.get_provider().get_name(hook.config)
    lock_key = "upsert:job:{build_id}:{provider}:{job_xid}".format(
        build_id=build.id, provider=provider_name, job_xid=external_id
    )
    with redis.lock(lock_key):
        json = data.copy() if data else {}
        json["external_id"] = external_id
        json["provider"] = provider_name
        json["hook_id"] = str(hook.id)

        job = Job.query.filter(
            Job.provider == provider_name,
            Job.external_id == external_id,
            Job.build_id == build.id,
        ).first()

        if job:
            return client.put(
                "/repos/{}/builds/{}/jobs/{}".format(
                    build.repository.get_full_name(), job.build.number, job.number
                ),
                json=json,
            )

        return client.post(
            "/repos/{}/builds/{}/jobs".format(
                build.repository.get_full_name(), build.number
            ),
            json=json,
        )


def upsert_build(hook: Hook, external_id: str, data: dict = None) -> Response:
    provider_name = hook.get_provider().get_name(hook.config)
    lock_key = "hook:build:{repo_id}:{provider}:{build_xid}".format(
        repo_id=hook.repository_id, provider=provider_name, build_xid=external_id
    )
    # TODO (here and in other upsert_* functions): it's better to move all the locking
    # code to async tasks.
    with redis.lock(lock_key, timeout=BUILD_LOCK_TIMEOUT):
        json = data.copy() if data else {}
        json["external_id"] = external_id
        json["provider"] = provider_name
        json["hook_id"] = str(hook.id)

        build = Build.query.filter(
            Build.provider == provider_name, Build.external_id == external_id
        ).first()

        if build:
            return client.put(
                "/repos/{}/builds/{}".format(
                    hook.repository.get_full_name(), build.number
                ),
                json=json,
            )

        return client.post(
            "/repos/{}/builds".format(hook.repository.get_full_name()), json=json
        )


def upsert_change_request(
    repository: Repository, provider: str, external_id: str, data: dict = None
) -> Response:
    lock_key = "hook:cr:{repo_id}:{provider}:{cr_xid}".format(
        repo_id=repository.id, provider=provider, cr_xid=external_id
    )
    with redis.lock(lock_key):
        json = data.copy() if data else {}
        json["external_id"] = external_id
        json["provider"] = provider

        cr = ChangeRequest.query.filter(
            ChangeRequest.repository_id == repository.id,
            ChangeRequest.provider == provider,
            ChangeRequest.external_id == external_id,
        ).first()

        if cr:
            return client.put(
                "/repos/{}/change-requests/{}".format(
                    repository.get_full_name(), cr.number
                ),
                json=json,
            )

        return client.post(
            "/repos/{}/change-requests".format(repository.get_full_name()), json=json
        )
