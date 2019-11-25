import dateutil.parser

from flask import current_app
from sqlalchemy.orm import joinedload
from urllib.parse import urlparse

from zeus import auth
from zeus.api.utils.upserts import upsert_build, upsert_change_request, upsert_job
from zeus.config import celery, nplusone
from zeus.constants import Permission
from zeus.exceptions import ApiError
from zeus.models import Build, Hook


def get_job_label(job: dict) -> str:
    job_config = job["config"]
    language = job_config["language"]
    language_version = job_config.get(language)
    out = []
    if language and language_version:
        out.append("{}: {}".format(language, language_version))
    else:
        out.append(language)
    if job_config.get("env"):
        out.append(" ".join(job_config["env"]))
    return " - ".join(out)


def get_result(state: str) -> str:
    return {
        "pending": "in_progress",
        "passed": "passed",
        "fixed": "passed",
        "failed": "failed",
        "broken": "failed",
        "failing": "failed",
        "errored": "failed",
        "canceled": "aborted",
    }.get(state, "unknown")


@celery.task(max_retries=5, autoretry_for=(Exception,), acks_late=True, time_limit=60)
def process_travis_webhook(hook_id: str, payload: dict, timestamp_ms: int):
    # TODO(dcramer): we want to utilize timestamp_ms to act as a version and
    # ensure we dont process older updates after newer updates are already present
    with nplusone.ignore("eager_load"):
        hook = (
            Hook.query.unrestricted_unsafe()
            .options(joinedload("repository"))
            .get(hook_id)
        )

    auth.set_current_tenant(auth.Tenant(access={hook.repository_id: Permission.admin}))

    data = {"ref": payload["commit"], "url": payload["build_url"]}

    domain = urlparse(data["url"]).netloc

    try:
        if payload["pull_request"]:
            data["label"] = "PR #{} - {}".format(
                payload["pull_request_number"], payload["pull_request_title"]
            )

            upsert_change_request(
                repository=hook.repository,
                provider="github",
                external_id=str(payload["pull_request_number"]),
                data={
                    "parent_ref": payload["base_commit"],
                    "head_ref": payload["head_commit"],
                    "message": payload["pull_request_title"],
                },
            )

        response = upsert_build(hook=hook, external_id=str(payload["id"]), data=data)
        build = Build.query.get(response.json()["id"])
        for job_payload in payload["matrix"]:
            upsert_job(
                build=build,
                hook=hook,
                external_id=str(job_payload["id"]),
                data={
                    "status": (
                        "finished"
                        if job_payload["status"] is not None
                        else "in_progress"
                    ),
                    "result": get_result(job_payload["state"]),
                    "allow_failure": bool(job_payload["allow_failure"]),
                    "label": get_job_label(job_payload),
                    "url": "https://{domain}/{owner}/{name}/jobs/{job_id}".format(
                        domain=domain,
                        owner=payload["repository"]["owner_name"],
                        name=payload["repository"]["name"],
                        job_id=job_payload["id"],
                    ),
                    "started_at": (
                        dateutil.parser.parse(job_payload["started_at"])
                        if job_payload["started_at"]
                        else None
                    ),
                    "finished_at": (
                        dateutil.parser.parse(job_payload["finished_at"])
                        if job_payload["finished_at"]
                        else None
                    ),
                },
            )
    except ApiError:
        current_app.logger.error("travis.webhook-unexpected-error", exc_info=True)
        raise
