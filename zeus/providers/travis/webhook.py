import json
import requests

from base64 import b64decode
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from flask import current_app, request, Response

from zeus.api.utils.upserts import upsert_build, upsert_job
from zeus.config import redis
from zeus.constants import USER_AGENT
from zeus.models import Build
from zeus.web.hooks.base import BaseHook


def get_result(state: str) -> str:
    return {
        'pending': 'in_progress',
        'passed': 'passed',
        'fixed': 'passed',
        'failed': 'failed',
        'broken': 'failed',
        'failing': 'failed',
        'errored': 'failed',
        'canceled': 'aborted',
    }.get(state, 'unknown')


def get_travis_public_key(domain) -> str:
    cache_key = 'travis:public-key:{}'.format(domain)
    public_key = redis.get(cache_key)
    if public_key is None:
        resp = requests.get(
            'https://{}/config'.format(domain),
            headers={'User-Agent': USER_AGENT},
        )
        resp.raise_for_status()
        public_key = resp.json()[
            'config']['notifications']['webhook']['public_key']
        redis.setex(cache_key, public_key, 300)
    return serialization.load_pem_public_key(public_key.encode('utf-8'), backend=default_backend())


def verify_signature(public_key, signature, payload):
    return public_key.verify(
        signature,
        payload,
        padding.PSS(mgf=padding.MGF1(hashes.SHA1()),
                    salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA1(),
    )


class TravisWebhookView(BaseHook):
    def post(self, hook):
        payload = request.form.get('payload')
        if not payload:
            current_app.logger.error('travis.missing-payload')
            return Response(status=400)

        signature = request.headers.get('Signature')
        if not signature:
            current_app.logger.error('travis.missing-signature')
            return Response(status=400)

        try:
            signature = b64decode(signature)
        except ValueError:
            current_app.logger.error('travis.invalid-signature', exc_info=True)
            return Response(status=400)

        # TODO(dcramer): use two separate providers for Travis private and travis public
        # and/or store the domain with the hook config
        public_key = get_travis_public_key('api.travis-ci.org')
        try:
            verify_signature(public_key, signature, payload.encode('utf-8'))
        except InvalidSignature:
            current_app.logger.error('travis.invalid-signature', exc_info=True)
            return Response(status=400)

        try:
            payload = json.loads(payload)
        except (TypeError, ValueError):
            current_app.logger.error('travis.invalid-payload', exc_info=True)
            return Response(status=400)

        data = {
            'ref': payload['commit'],
        }

        if payload['pull_request']:
            data['label'] = 'PR #{}'.format(payload['pull_request_number'])

        response = upsert_build(
            repository=hook.repository,
            provider=hook.provider,
            external_id=str(payload['id']),
            data=data,
        )
        build = Build.query.get(response.json()['id'])
        for job_payload in payload['matrix']:
            upsert_job(
                build=build,
                provider=hook.provider,
                external_id=str(job_payload['id']),
                data={
                    'status': 'finished' if job_payload['status'] is not None else 'in_progress',
                    'result': get_result(job_payload['state']),
                }
            )

        return Response(status=200)
