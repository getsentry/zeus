from flask import Response

from zeus.config import redis
from zeus.models import Repository, Build, ChangeRequest, Job
from zeus.api import client


def upsert_job(
    build: Build, provider: str, external_id: str, data: dict = None
) -> Response:
    lock_key = "upsert:job:{build_id}:{provider}:{job_xid}".format(
        build_id=build.id, provider=provider, job_xid=external_id
    )
    with redis.lock(lock_key):
        json = data.copy() if data else {}
        json["external_id"] = external_id
        json["provider"] = provider

        job = Job.query.filter(
            Job.provider == provider,
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


def upsert_build(
    repository: Repository, provider: str, external_id: str, data: dict = None
) -> Response:
    lock_key = "hook:build:{repo_id}:{provider}:{build_xid}".format(
        repo_id=repository.id, provider=provider, build_xid=external_id
    )
    with redis.lock(lock_key):
        json = data.copy() if data else {}
        json["external_id"] = external_id
        json["provider"] = provider

        build = Build.query.filter(
            Build.provider == provider, Build.external_id == external_id
        ).first()

        if build:
            return client.put(
                "/repos/{}/builds/{}".format(repository.get_full_name(), build.number),
                json=json,
            )

        return client.post(
            "/repos/{}/builds".format(repository.get_full_name()), json=json
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
            ChangeRequest.provider == provider, ChangeRequest.external_id == external_id
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
