import json
import requests

from base64 import b64decode
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from flask import current_app, request, Response
from time import time

from zeus.config import celery, redis
from zeus.constants import USER_AGENT
from zeus.web.hooks.base import BaseHook


def get_travis_public_key(domain) -> str:
    cache_key = "travis:public-key:{}".format(domain)
    public_key = redis.get(cache_key)
    if public_key is None:
        resp = requests.get(
            "https://{}/config".format(domain), headers={"User-Agent": USER_AGENT}
        )
        resp.raise_for_status()
        public_key = resp.json()["config"]["notifications"]["webhook"][
            "public_key"
        ].encode("utf-8")
        redis.setex(cache_key, 300, public_key)
    return serialization.load_pem_public_key(public_key, backend=default_backend())


def verify_signature(public_key, signature, payload):
    return public_key.verify(signature, payload, padding.PKCS1v15(), hashes.SHA1())


class TravisWebhookView(BaseHook):
    public = True

    def get(self, hook):
        return Response(status=405)

    def post(self, hook):
        current_app.logger.info("travis.received-webhook")

        payload = request.form.get("payload")
        if not payload:
            current_app.logger.error("travis.webhook-missing-payload")
            return Response(status=400)

        signature = request.headers.get("Signature")
        if not signature:
            current_app.logger.error("travis.webhook-missing-signature")
            return Response(status=400)

        try:
            signature = b64decode(signature)
        except ValueError:
            current_app.logger.error("travis.webhook-invalid-signature", exc_info=True)
            return Response(status=400)

        api_domain = (hook.config or {}).get("domain", "api.travis-ci.org")
        public_key = get_travis_public_key(api_domain)
        try:
            verify_signature(public_key, signature, payload.encode("utf-8"))
        except InvalidSignature:
            current_app.logger.error("travis.webhook-invalid-signature", exc_info=True)
            return Response(status=400)

        try:
            payload = json.loads(payload)
        except (TypeError, ValueError):
            current_app.logger.error("travis.webhook-invalid-payload", exc_info=True)
            return Response(status=400)

        current_app.logger.info(
            "travis.webhook-validated",
            extra={
                "build_id": payload["id"],
                "build_url": payload["build_url"],
                "commit_sha": payload["commit"],
            },
        )

        try:
            celery.call(
                "zeus.process_travis_webhook",
                hook_id=hook.id,
                payload=payload,
                timestamp_ms=int(time() * 1000),
            )
        except Exception:
            current_app.logger.error("travis.process-webhook-failed", exc_info=True)
            celery.delay(
                "zeus.process_travis_webhook",
                hook_id=hook.id,
                payload=payload,
                timestamp_ms=int(time() * 1000),
            )

        return Response(status=202)
